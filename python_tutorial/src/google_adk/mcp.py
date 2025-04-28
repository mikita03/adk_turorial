"""
Model Contexts Protocol (MCP) for Google Agent Development Kit (ADK)

このモジュールは、Google ADKのためのModel Contexts Protocol (MCP)の実装を提供します。
MCPは、エージェントが異なるコンテキストを管理し、それらの間で情報を共有するための
プロトコルです。

MCPを使用することで、エージェントは:
1. 複数のコンテキストを作成・管理できる
2. コンテキスト内に情報を保存できる
3. コンテキストから情報を取得できる
4. 異なるコンテキスト間で切り替えができる
5. コンテキスト間で情報を共有できる

これにより、エージェントはより複雑なタスクを実行し、長期的な会話や
マルチステップのタスクをより効果的に管理できるようになります。
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger("ADK-MCP")

class Context:
    """
    MCPのコンテキストを表すクラス
    
    コンテキストは、特定の会話やタスクに関連する情報を保持します。
    """
    
    def __init__(
        self,
        context_id: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Contextクラスの初期化
        
        Args:
            context_id: コンテキストの一意識別子
            name: コンテキストの名前
            description: コンテキストの説明（オプション）
            metadata: コンテキストに関連するメタデータ（オプション）
        """
        self.context_id = context_id
        self.name = name
        self.description = description or f"Context: {name}"
        self.metadata = metadata or {}
        self.data = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        
        logger.info(f"コンテキスト '{self.name}' (ID: {self.context_id}) が作成されました")
    
    def set_value(self, key: str, value: Any) -> None:
        """
        コンテキストに値を設定する
        
        Args:
            key: 値のキー
            value: 設定する値
        """
        self.data[key] = value
        self.updated_at = datetime.now().isoformat()
        logger.debug(f"コンテキスト '{self.name}' にキー '{key}' の値を設定しました")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        コンテキストから値を取得する
        
        Args:
            key: 値のキー
            default: キーが存在しない場合のデフォルト値
            
        Returns:
            キーに関連付けられた値、またはデフォルト値
        """
        return self.data.get(key, default)
    
    def delete_value(self, key: str) -> bool:
        """
        コンテキストから値を削除する
        
        Args:
            key: 削除する値のキー
            
        Returns:
            削除が成功したかどうか
        """
        if key in self.data:
            del self.data[key]
            self.updated_at = datetime.now().isoformat()
            logger.debug(f"コンテキスト '{self.name}' からキー '{key}' を削除しました")
            return True
        return False
    
    def clear(self) -> None:
        """コンテキストのすべての値をクリアする"""
        self.data = {}
        self.updated_at = datetime.now().isoformat()
        logger.debug(f"コンテキスト '{self.name}' のすべての値をクリアしました")
    
    def to_dict(self) -> Dict[str, Any]:
        """コンテキストを辞書形式で返す"""
        return {
            "context_id": self.context_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "data": self.data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """辞書からコンテキストを作成する"""
        context = cls(
            context_id=data["context_id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )
        context.data = data.get("data", {})
        context.created_at = data.get("created_at", context.created_at)
        context.updated_at = data.get("updated_at", context.updated_at)
        return context


class ModelContextsProtocol:
    """
    Model Contexts Protocol (MCP)の実装
    
    このクラスは、複数のコンテキストを管理し、それらの間で情報を共有するための
    機能を提供します。
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        ModelContextsProtocolクラスの初期化
        
        Args:
            storage_path: コンテキストを保存するディレクトリのパス（オプション）
        """
        self.contexts: Dict[str, Context] = {}
        self.active_context_id: Optional[str] = None
        self.storage_path = storage_path
        
        if self.storage_path and os.path.exists(self.storage_path):
            self._load_contexts()
        
        logger.info("Model Contexts Protocol (MCP) が初期化されました")
    
    def create_context(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        make_active: bool = True
    ) -> Context:
        """
        新しいコンテキストを作成する
        
        Args:
            name: コンテキストの名前
            description: コンテキストの説明（オプション）
            metadata: コンテキストに関連するメタデータ（オプション）
            make_active: 作成したコンテキストをアクティブにするかどうか
            
        Returns:
            作成されたコンテキスト
        """
        import uuid
        context_id = str(uuid.uuid4())
        context = Context(context_id, name, description, metadata)
        self.contexts[context_id] = context
        
        if make_active:
            self.active_context_id = context_id
            logger.info(f"コンテキスト '{name}' (ID: {context_id}) を作成し、アクティブにしました")
        else:
            logger.info(f"コンテキスト '{name}' (ID: {context_id}) を作成しました")
        
        if self.storage_path:
            self._save_contexts()
        
        return context
    
    def get_context(self, context_id: str) -> Optional[Context]:
        """
        指定されたIDのコンテキストを取得する
        
        Args:
            context_id: 取得するコンテキストのID
            
        Returns:
            コンテキスト、または存在しない場合はNone
        """
        return self.contexts.get(context_id)
    
    def get_context_by_name(self, name: str) -> Optional[Context]:
        """
        指定された名前のコンテキストを取得する
        
        Args:
            name: 取得するコンテキストの名前
            
        Returns:
            コンテキスト、または存在しない場合はNone
        """
        for context in self.contexts.values():
            if context.name == name:
                return context
        return None
    
    def list_contexts(self) -> List[Dict[str, Any]]:
        """
        すべてのコンテキストのリストを取得する
        
        Returns:
            コンテキスト情報のリスト
        """
        return [
            {
                "context_id": context.context_id,
                "name": context.name,
                "description": context.description,
                "is_active": context.context_id == self.active_context_id
            }
            for context in self.contexts.values()
        ]
    
    def set_active_context(self, context_id: str) -> bool:
        """
        アクティブなコンテキストを設定する
        
        Args:
            context_id: アクティブにするコンテキストのID
            
        Returns:
            設定が成功したかどうか
        """
        if context_id in self.contexts:
            self.active_context_id = context_id
            context = self.contexts[context_id]
            logger.info(f"コンテキスト '{context.name}' (ID: {context_id}) をアクティブにしました")
            return True
        
        logger.warning(f"コンテキスト ID '{context_id}' が見つかりません")
        return False
    
    def get_active_context(self) -> Optional[Context]:
        """
        現在アクティブなコンテキストを取得する
        
        Returns:
            アクティブなコンテキスト、または存在しない場合はNone
        """
        if self.active_context_id:
            return self.contexts.get(self.active_context_id)
        return None
    
    def delete_context(self, context_id: str) -> bool:
        """
        コンテキストを削除する
        
        Args:
            context_id: 削除するコンテキストのID
            
        Returns:
            削除が成功したかどうか
        """
        if context_id in self.contexts:
            context = self.contexts[context_id]
            del self.contexts[context_id]
            
            if self.active_context_id == context_id:
                self.active_context_id = next(iter(self.contexts)) if self.contexts else None
            
            logger.info(f"コンテキスト '{context.name}' (ID: {context_id}) を削除しました")
            
            if self.storage_path:
                self._save_contexts()
            
            return True
        
        logger.warning(f"コンテキスト ID '{context_id}' が見つかりません")
        return False
    
    def set_value(self, key: str, value: Any, context_id: Optional[str] = None) -> bool:
        """
        コンテキストに値を設定する
        
        Args:
            key: 値のキー
            value: 設定する値
            context_id: 値を設定するコンテキストのID（指定しない場合はアクティブなコンテキスト）
            
        Returns:
            設定が成功したかどうか
        """
        context = self._get_target_context(context_id)
        if context:
            context.set_value(key, value)
            
            if self.storage_path:
                self._save_contexts()
            
            return True
        
        return False
    
    def get_value(self, key: str, default: Any = None, context_id: Optional[str] = None) -> Any:
        """
        コンテキストから値を取得する
        
        Args:
            key: 値のキー
            default: キーが存在しない場合のデフォルト値
            context_id: 値を取得するコンテキストのID（指定しない場合はアクティブなコンテキスト）
            
        Returns:
            キーに関連付けられた値、またはデフォルト値
        """
        context = self._get_target_context(context_id)
        if context:
            return context.get_value(key, default)
        
        return default
    
    def delete_value(self, key: str, context_id: Optional[str] = None) -> bool:
        """
        コンテキストから値を削除する
        
        Args:
            key: 削除する値のキー
            context_id: 値を削除するコンテキストのID（指定しない場合はアクティブなコンテキスト）
            
        Returns:
            削除が成功したかどうか
        """
        context = self._get_target_context(context_id)
        if context:
            result = context.delete_value(key)
            
            if result and self.storage_path:
                self._save_contexts()
            
            return result
        
        return False
    
    def copy_value(
        self,
        key: str,
        source_context_id: str,
        target_context_id: str,
        new_key: Optional[str] = None
    ) -> bool:
        """
        あるコンテキストから別のコンテキストに値をコピーする
        
        Args:
            key: コピーする値のキー
            source_context_id: コピー元のコンテキストID
            target_context_id: コピー先のコンテキストID
            new_key: コピー先での新しいキー（指定しない場合は元のキーを使用）
            
        Returns:
            コピーが成功したかどうか
        """
        source_context = self.get_context(source_context_id)
        target_context = self.get_context(target_context_id)
        
        if not source_context:
            logger.warning(f"コピー元のコンテキスト ID '{source_context_id}' が見つかりません")
            return False
        
        if not target_context:
            logger.warning(f"コピー先のコンテキスト ID '{target_context_id}' が見つかりません")
            return False
        
        if key not in source_context.data:
            logger.warning(f"キー '{key}' がコンテキスト '{source_context.name}' に存在しません")
            return False
        
        value = source_context.get_value(key)
        target_key = new_key or key
        target_context.set_value(target_key, value)
        
        logger.info(
            f"値をコピーしました: '{source_context.name}' の '{key}' から "
            f"'{target_context.name}' の '{target_key}' へ"
        )
        
        if self.storage_path:
            self._save_contexts()
        
        return True
    
    def _get_target_context(self, context_id: Optional[str] = None) -> Optional[Context]:
        """
        指定されたIDまたはアクティブなコンテキストを取得する
        
        Args:
            context_id: コンテキストID（指定しない場合はアクティブなコンテキスト）
            
        Returns:
            コンテキスト、または存在しない場合はNone
        """
        if context_id:
            context = self.get_context(context_id)
            if not context:
                logger.warning(f"コンテキスト ID '{context_id}' が見つかりません")
                return None
            return context
        
        context = self.get_active_context()
        if not context:
            logger.warning("アクティブなコンテキストが設定されていません")
            return None
        
        return context
    
    def _save_contexts(self) -> None:
        """コンテキストをファイルに保存する"""
        if not self.storage_path:
            return
        
        os.makedirs(self.storage_path, exist_ok=True)
        file_path = os.path.join(self.storage_path, "mcp_contexts.json")
        
        data = {
            "active_context_id": self.active_context_id,
            "contexts": {
                context_id: context.to_dict()
                for context_id, context in self.contexts.items()
            }
        }
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"コンテキストを '{file_path}' に保存しました")
        except Exception as e:
            logger.error(f"コンテキストの保存中にエラーが発生しました: {e}")
    
    def _load_contexts(self) -> None:
        """コンテキストをファイルから読み込む"""
        if not self.storage_path:
            return
        
        file_path = os.path.join(self.storage_path, "mcp_contexts.json")
        
        if not os.path.exists(file_path):
            logger.debug(f"コンテキストファイル '{file_path}' が見つかりません")
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.active_context_id = data.get("active_context_id")
            
            for context_id, context_data in data.get("contexts", {}).items():
                self.contexts[context_id] = Context.from_dict(context_data)
            
            logger.debug(f"コンテキストを '{file_path}' から読み込みました")
        except Exception as e:
            logger.error(f"コンテキストの読み込み中にエラーが発生しました: {e}")



def create_context(name: str, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    新しいコンテキストを作成する
    
    Args:
        name: コンテキストの名前
        description: コンテキストの説明（オプション）
        metadata: コンテキストに関連するメタデータ（オプション）
        
    Returns:
        作成されたコンテキストの情報
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    context = _mcp_instance.create_context(name, description, metadata)
    
    return {
        "context_id": context.context_id,
        "name": context.name,
        "description": context.description,
        "is_active": context.context_id == _mcp_instance.active_context_id
    }


def list_contexts() -> List[Dict[str, Any]]:
    """
    すべてのコンテキストのリストを取得する
    
    Returns:
        コンテキスト情報のリスト
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    return _mcp_instance.list_contexts()


def set_active_context(context_id: str) -> Dict[str, Any]:
    """
    アクティブなコンテキストを設定する
    
    Args:
        context_id: アクティブにするコンテキストのID
        
    Returns:
        操作の結果
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    success = _mcp_instance.set_active_context(context_id)
    
    if success:
        context = _mcp_instance.get_context(context_id)
        return {
            "success": True,
            "context_id": context.context_id,
            "name": context.name,
            "description": context.description
        }
    
    return {
        "success": False,
        "error": f"コンテキスト ID '{context_id}' が見つかりません"
    }


def get_active_context() -> Dict[str, Any]:
    """
    現在アクティブなコンテキストを取得する
    
    Returns:
        アクティブなコンテキストの情報
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    context = _mcp_instance.get_active_context()
    
    if context:
        return {
            "context_id": context.context_id,
            "name": context.name,
            "description": context.description,
            "data": context.data
        }
    
    return {
        "error": "アクティブなコンテキストが設定されていません"
    }


def set_context_value(key: str, value: Any, context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    コンテキストに値を設定する
    
    Args:
        key: 値のキー
        value: 設定する値
        context_id: 値を設定するコンテキストのID（指定しない場合はアクティブなコンテキスト）
        
    Returns:
        操作の結果
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    success = _mcp_instance.set_value(key, value, context_id)
    
    if success:
        context = _mcp_instance.get_context(context_id) if context_id else _mcp_instance.get_active_context()
        return {
            "success": True,
            "context_id": context.context_id,
            "name": context.name,
            "key": key
        }
    
    return {
        "success": False,
        "error": "値の設定に失敗しました"
    }


def get_context_value(key: str, context_id: Optional[str] = None) -> Any:
    """
    コンテキストから値を取得する
    
    Args:
        key: 値のキー
        context_id: 値を取得するコンテキストのID（指定しない場合はアクティブなコンテキスト）
        
    Returns:
        取得した値、またはコンテキストやキーが存在しない場合はNone
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    context = _mcp_instance.get_context(context_id) if context_id else _mcp_instance.get_active_context()
    
    if not context:
        logger.warning("コンテキストが見つかりません")
        return None
    
    if key in context.data:
        return context.get_value(key)
    
    logger.warning(f"キー '{key}' がコンテキスト '{context.name}' に存在しません")
    return None


def delete_context(context_id: str) -> Dict[str, Any]:
    """
    コンテキストを削除する
    
    Args:
        context_id: 削除するコンテキストのID
        
    Returns:
        操作の結果
    """
    global _mcp_instance
    if _mcp_instance is None:
        _initialize_mcp()
    
    context = _mcp_instance.get_context(context_id)
    
    if not context:
        return {
            "success": False,
            "error": f"コンテキスト ID '{context_id}' が見つかりません"
        }
    
    context_name = context.name
    success = _mcp_instance.delete_context(context_id)
    
    return {
        "success": success,
        "context_id": context_id,
        "name": context_name
    }


_mcp_instance = None


def _initialize_mcp(storage_path: Optional[str] = None) -> None:
    """
    グローバルなMCPインスタンスを初期化する
    
    Args:
        storage_path: コンテキストを保存するディレクトリのパス（オプション）
    """
    global _mcp_instance
    _mcp_instance = ModelContextsProtocol(storage_path)
    
    if not _mcp_instance.contexts:
        _mcp_instance.create_context(
            name="デフォルト",
            description="デフォルトのコンテキスト",
            metadata={"type": "default"}
        )


_initialize_mcp()
