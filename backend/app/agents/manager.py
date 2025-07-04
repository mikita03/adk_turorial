import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import json
from datetime import datetime

from ..schemas.email import EmailContent

logger = logging.getLogger(__name__)

class ManagerAgent:
    def __init__(self, llm_model: str = "gpt-4"):
        logger.info(f"Initializing ManagerAgent with model: {llm_model}")
        try:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
            logger.info("ManagerAgent ChatOpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ManagerAgent ChatOpenAI: {e}")
            raise
        self.role = """
        あなたはファイル管理の専門エージェントです。
        添付ファイルの自動保存、プロジェクトごとのフォルダ振り分け、
        メタデータ管理を行います。
        """
    
    async def manage_attachments(self, email: EmailContent) -> Dict[str, Any]:
        """Manage email attachments"""
        
        if not email.attachments:
            return {
                "success": True,
                "message": "添付ファイルはありません",
                "files_processed": 0,
                "processing_time": 0.0
            }
        
        try:
            organization_plan = await self._analyze_attachments(email)
            
            processed_files = []
            for attachment in email.attachments:
                file_info = await self._process_attachment(attachment, organization_plan)
                processed_files.append(file_info)
            
            return {
                "success": True,
                "files_processed": len(processed_files),
                "processed_files": processed_files,
                "organization_plan": organization_plan,
                "processing_time": 0.0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "files_processed": 0,
                "processing_time": 0.0
            }
    
    async def _analyze_attachments(self, email: EmailContent) -> Dict[str, Any]:
        """Analyze attachments and determine organization strategy"""
        
        attachment_info = []
        for attachment in email.attachments:
            attachment_info.append({
                "filename": attachment.get("filename", "unknown"),
                "size": attachment.get("size", 0),
                "type": attachment.get("mimeType", "unknown")
            })
        
        analysis_prompt = f"""
        以下のメールの添付ファイルを分析し、適切な整理方法を決定してください。

        メール情報:
        - 送信者: {email.from_email}
        - 件名: {email.subject}
        - 本文: {email.body[:300]}...

        添付ファイル:
        {json.dumps(attachment_info, ensure_ascii=False, indent=2)}

        以下の観点で分析してください:
        1. プロジェクト/案件の特定
        2. ファイルタイプ別の分類
        3. 重要度の判定
        4. 保存先フォルダの提案

        以下のJSON形式で回答してください:
        {{
            "project_name": "プロジェクト名",
            "folder_structure": {{
                "main_folder": "メインフォルダ名",
                "sub_folders": ["サブフォルダ1", "サブフォルダ2"]
            }},
            "file_classifications": [
                {{
                    "filename": "ファイル名",
                    "category": "契約書|資料|画像|その他",
                    "importance": "high|medium|low",
                    "suggested_folder": "保存先フォルダ"
                }}
            ],
            "metadata_tags": ["タグ1", "タグ2"]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
            return json.loads(response.content)
        except:
            return {
                "project_name": "一般",
                "folder_structure": {
                    "main_folder": f"メール_{datetime.now().strftime('%Y%m%d')}",
                    "sub_folders": ["添付ファイル"]
                },
                "file_classifications": [
                    {
                        "filename": att.get("filename", "unknown"),
                        "category": "その他",
                        "importance": "medium",
                        "suggested_folder": "添付ファイル"
                    }
                    for att in email.attachments
                ],
                "metadata_tags": ["メール添付"]
            }
    
    async def _process_attachment(self, attachment: Dict[str, Any], organization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual attachment"""
        
        filename = attachment.get("filename", "unknown_file")
        file_size = attachment.get("size", 0)
        mime_type = attachment.get("mimeType", "unknown")
        
        file_classification = None
        for classification in organization_plan.get("file_classifications", []):
            if classification["filename"] == filename:
                file_classification = classification
                break
        
        if not file_classification:
            file_classification = {
                "filename": filename,
                "category": "その他",
                "importance": "medium",
                "suggested_folder": "添付ファイル"
            }
        
        processed_info = {
            "original_filename": filename,
            "processed_filename": f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}",
            "file_size": file_size,
            "mime_type": mime_type,
            "category": file_classification["category"],
            "importance": file_classification["importance"],
            "saved_location": f"{organization_plan['folder_structure']['main_folder']}/{file_classification['suggested_folder']}/{filename}",
            "metadata": {
                "processed_date": datetime.now().isoformat(),
                "source_email": "email_id_placeholder",
                "tags": organization_plan.get("metadata_tags", [])
            }
        }
        
        return processed_info
    
    async def create_folder_structure(self, organization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create folder structure (placeholder for Google Drive integration)"""
        
        try:
            main_folder = organization_plan["folder_structure"]["main_folder"]
            sub_folders = organization_plan["folder_structure"]["sub_folders"]
            
            created_folders = {
                "main_folder": {
                    "name": main_folder,
                    "id": f"folder_{datetime.now().timestamp()}",
                    "created": True
                },
                "sub_folders": []
            }
            
            for sub_folder in sub_folders:
                created_folders["sub_folders"].append({
                    "name": sub_folder,
                    "id": f"subfolder_{datetime.now().timestamp()}_{sub_folder}",
                    "parent": main_folder,
                    "created": True
                })
            
            return {
                "success": True,
                "created_folders": created_folders
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_file_summary(self, processed_files: List[Dict[str, Any]]) -> str:
        """Generate summary of processed files"""
        
        if not processed_files:
            return "添付ファイルはありませんでした。"
        
        summary_prompt = f"""
        以下の処理されたファイル情報から、簡潔な要約を作成してください。

        処理ファイル:
        {json.dumps(processed_files, ensure_ascii=False, indent=2)}

        以下の形式で要約してください:
        - 処理ファイル数: X件
        - 主なファイルタイプ: 
        - 重要度高のファイル: 
        - 保存先: 
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
            return response.content
        except:
            file_count = len(processed_files)
            categories = list(set([f.get("category", "その他") for f in processed_files]))
            return f"添付ファイル{file_count}件を処理しました。カテゴリ: {', '.join(categories)}"
