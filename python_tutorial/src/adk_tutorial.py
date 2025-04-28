
"""
Android Accessory Development Kit (ADK) Tutorial

このファイルはAndroid Accessory Development Kit (ADK)の基本的な使い方を示すチュートリアルです。
ADKを使用して、Androidデバイスと外部アクセサリ（ハードウェア）を接続する方法を説明します。

ADKは、Android Open Accessory (AOA) プロトコルを使用して、外部ハードウェアとAndroidデバイスの
通信を可能にします。このチュートリアルでは、ADKの基本概念、接続方法、およびデータ通信の
実装方法について説明します。

注意: このコードを実行するには、実際のADKハードウェアが必要です。このチュートリアルは
主に教育目的で、実際のハードウェアがなくてもADKの概念を理解できるようにシミュレーション
機能を含んでいます。
"""

import os
import sys
import time
import random
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ADK_Tutorial")


class ConnectionType(Enum):
    """
    アクセサリの接続タイプを表す列挙型
    
    USB: USB接続を使用
    BLUETOOTH: Bluetooth接続を使用
    """
    USB = "usb"
    BLUETOOTH = "bluetooth"


class ProtocolVersion(Enum):
    """
    AOAプロトコルのバージョンを表す列挙型
    
    AOAv1: Android 3.1 (API 12)で導入された最初のバージョン
    AOAv2: Android 4.1 (API 16)で導入された拡張バージョン（オーディオサポートとHID機能を追加）
    """
    AOAv1 = "aoav1"
    AOAv2 = "aoav2"


class AccessoryDevice:
    """
    Androidアクセサリデバイスを表すクラス
    
    このクラスは、Androidデバイスに接続するアクセサリの基本情報と機能を定義します。
    実際のハードウェアの代わりに、シミュレーションされたアクセサリとして機能します。
    """
    
    def __init__(
        self,
        device_id: str,
        name: str,
        manufacturer: str,
        description: str,
        version: str,
        uri: str,
        serial_number: str,
        connection_type: ConnectionType,
        protocol_version: ProtocolVersion
    ):
        """
        アクセサリデバイスの初期化
        
        Args:
            device_id: デバイスの一意識別子
            name: デバイスの名前
            manufacturer: 製造元
            description: デバイスの説明
            version: バージョン番号
            uri: 製造元のWebサイトなど
            serial_number: シリアル番号
            connection_type: 接続タイプ（USB/Bluetooth）
            protocol_version: AOAプロトコルのバージョン
        """
        self.device_id = device_id
        self.name = name
        self.manufacturer = manufacturer
        self.description = description
        self.version = version
        self.uri = uri
        self.serial_number = serial_number
        self.connection_type = connection_type
        self.protocol_version = protocol_version
        self.connected = False
        self.features = []
        
        logger.info(f"アクセサリデバイス '{self.name}' が初期化されました")
    
    def connect(self) -> bool:
        """
        アクセサリをAndroidデバイスに接続する
        
        実際のハードウェアでは、ここでUSBまたはBluetoothの接続処理を行います。
        このシミュレーションでは、接続状態を変更するだけです。
        
        Returns:
            bool: 接続が成功したかどうか
        """
        if not self.connected:
            logger.info(f"アクセサリ '{self.name}' を接続しています...")
            time.sleep(1)
            self.connected = True
            logger.info(f"アクセサリ '{self.name}' が正常に接続されました")
            return True
        else:
            logger.warning(f"アクセサリ '{self.name}' は既に接続されています")
            return False
    
    def disconnect(self) -> bool:
        """
        アクセサリをAndroidデバイスから切断する
        
        実際のハードウェアでは、ここでUSBまたはBluetoothの切断処理を行います。
        このシミュレーションでは、接続状態を変更するだけです。
        
        Returns:
            bool: 切断が成功したかどうか
        """
        if self.connected:
            logger.info(f"アクセサリ '{self.name}' を切断しています...")
            time.sleep(0.5)
            self.connected = False
            logger.info(f"アクセサリ '{self.name}' が正常に切断されました")
            return True
        else:
            logger.warning(f"アクセサリ '{self.name}' は既に切断されています")
            return False
    
    def send_command(self, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        アクセサリにコマンドを送信する
        
        実際のハードウェアでは、ここでUSBまたはBluetoothを介してコマンドを送信します。
        このシミュレーションでは、コマンドの処理をシミュレートします。
        
        Args:
            command: 送信するコマンド
            params: コマンドのパラメータ（オプション）
            
        Returns:
            Dict[str, Any]: コマンドの応答
        """
        if not self.connected:
            logger.error(f"アクセサリ '{self.name}' は接続されていないため、コマンドを送信できません")
            return {"status": "error", "message": "デバイスが接続されていません"}
        
        params = params.copy()
            
        logger.info(f"アクセサリ '{self.name}' にコマンド '{command}' を送信しています（パラメータ: {params}）")
        
        time.sleep(0.3)
        
        return {"status": "success", "message": "コマンドが処理されました"}
    
    def get_info(self) -> Dict[str, Any]:
        """
        アクセサリの情報を取得する
        
        Returns:
            Dict[str, Any]: アクセサリの情報
        """
        return {
            "device_id": self.device_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "description": self.description,
            "version": self.version,
            "uri": self.uri,
            "serial_number": self.serial_number,
            "connection_type": self.connection_type.value,
            "protocol_version": self.protocol_version.value,
            "connected": self.connected,
            "features": self.features
        }



class LEDController(AccessoryDevice):
    """
    LED制御アクセサリ
    
    このクラスは、LEDライトを制御するアクセサリをシミュレートします。
    明るさ、色、点滅パターンなどの制御が可能です。
    """
    
    def __init__(self):
        """LEDコントローラの初期化"""
        super().__init__(
            device_id="led_controller_001",
            name="RGB LED Controller",
            manufacturer="ADK Tutorial",
            description="RGB LED controller for Android devices",
            version="1.0",
            uri="https://example.com/adk/led",
            serial_number="LED00123456789",
            connection_type=ConnectionType.USB,
            protocol_version=ProtocolVersion.AOAv2
        )
        
        self.features = ["color_control", "brightness_control", "pattern_selection"]
        
        self.state = {
            "brightness": 50,  # 0-100%
            "color": "#FFFFFF",  # HEX形式の色
            "pattern": "solid",  # solid, blink, pulse, rainbow
            "power": False  # オン/オフ状態
        }
        
        logger.info("LEDコントローラが初期化されました")
    
    def send_command(self, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        LEDコントローラにコマンドを送信する
        
        Args:
            command: 送信するコマンド（set_brightness, set_color, set_pattern, power）
            params: コマンドのパラメータ
            
        Returns:
            Dict[str, Any]: コマンドの応答
        """
        if not self.connected:
            return {"status": "error", "message": "デバイスが接続されていません"}
        
        params = params.copy()
            
        response = {"status": "success", "data": {}}
        
        if command == "set_brightness":
            if "value" in params and 0 <= params["value"] <= 100:
                self.state["brightness"] = params["value"]
                logger.info(f"明るさを {params['value']}% に設定しました")
                response["data"]["brightness"] = self.state["brightness"]
            else:
                response = {"status": "error", "message": "無効な明るさの値です（0-100の範囲で指定してください）"}
                
        elif command == "set_color":
            if "value" in params and params["value"].startswith("#") and len(params["value"]) == 7:
                self.state["color"] = params["value"]
                logger.info(f"色を {params['value']} に設定しました")
                response["data"]["color"] = self.state["color"]
            else:
                response = {"status": "error", "message": "無効な色の値です（#RRGGBBの形式で指定してください）"}
                
        elif command == "set_pattern":
            valid_patterns = ["solid", "blink", "pulse", "rainbow"]
            if "value" in params and params["value"] in valid_patterns:
                self.state["pattern"] = params["value"]
                logger.info(f"パターンを {params['value']} に設定しました")
                response["data"]["pattern"] = self.state["pattern"]
            else:
                response = {
                    "status": "error", 
                    "message": f"無効なパターンです（{', '.join(valid_patterns)}のいずれかを指定してください）"
                }
                
        elif command == "power":
            if "value" in params and isinstance(params["value"], bool):
                self.state["power"] = params["value"]
                status = "オン" if params["value"] else "オフ"
                logger.info(f"電源を{status}にしました")
                response["data"]["power"] = self.state["power"]
            else:
                response = {"status": "error", "message": "無効な電源の値です（trueまたはfalseを指定してください）"}
                
        else:
            response = {"status": "error", "message": f"未知のコマンド: {command}"}
            
        return response
    
    def get_state(self) -> Dict[str, Any]:
        """
        LEDコントローラの現在の状態を取得する
        
        Returns:
            Dict[str, Any]: LEDコントローラの状態
        """
        return self.state


class TemperatureSensor(AccessoryDevice):
    """
    温度センサーアクセサリ
    
    このクラスは、温度と湿度を測定するセンサーアクセサリをシミュレートします。
    """
    
    def __init__(self):
        """温度センサーの初期化"""
        super().__init__(
            device_id="temp_sensor_001",
            name="Temperature & Humidity Sensor",
            manufacturer="ADK Tutorial",
            description="Temperature and humidity sensor for Android devices",
            version="1.0",
            uri="https://example.com/adk/temp",
            serial_number="TEMP00123456789",
            connection_type=ConnectionType.BLUETOOTH,
            protocol_version=ProtocolVersion.AOAv1
        )
        
        self.features = ["temperature_reading", "humidity_reading", "data_logging"]
        
        self.state = {
            "temperature": 25.0,  # 摂氏
            "humidity": 50.0,     # %
            "last_updated": time.time()
        }
        
        self.data_log = []
        
        logger.info("温度センサーが初期化されました")
    
    def send_command(self, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        温度センサーにコマンドを送信する
        
        Args:
            command: 送信するコマンド（read_temperature, read_humidity, start_logging, stop_logging）
            params: コマンドのパラメータ
            
        Returns:
            Dict[str, Any]: コマンドの応答
        """
        if not self.connected:
            return {"status": "error", "message": "デバイスが接続されていません"}
        
        params = params.copy()
            
        response = {"status": "success", "data": {}}
        
        self._simulate_sensor_readings()
        
        if command == "read_temperature":
            logger.info(f"現在の温度: {self.state['temperature']}°C")
            response["data"]["temperature"] = self.state["temperature"]
                
        elif command == "read_humidity":
            logger.info(f"現在の湿度: {self.state['humidity']}%")
            response["data"]["humidity"] = self.state["humidity"]
                
        elif command == "start_logging":
            interval = params.get("interval", 60)  # デフォルトは60秒
            logger.info(f"データログを開始しました（間隔: {interval}秒）")
            response["data"]["logging"] = True
            response["data"]["interval"] = interval
                
        elif command == "stop_logging":
            logger.info("データログを停止しました")
            response["data"]["logging"] = False
                
        else:
            response = {"status": "error", "message": f"未知のコマンド: {command}"}
            
        return response
    
    def _simulate_sensor_readings(self):
        """センサーの読み取り値をシミュレートする"""
        current_time = time.time()
        if current_time - self.state["last_updated"] > 5:  # 5秒ごとに更新
            self.state["temperature"] = round(self.state["temperature"] + random.uniform(-0.5, 0.5), 1)
            self.state["humidity"] = round(self.state["humidity"] + random.uniform(-1, 1), 1)
            
            self.state["temperature"] = max(min(self.state["temperature"], 40), 10)
            self.state["humidity"] = max(min(self.state["humidity"], 100), 0)
            
            self.state["last_updated"] = current_time
            
            self.data_log.append({
                "timestamp": current_time,
                "temperature": self.state["temperature"],
                "humidity": self.state["humidity"]
            })
            
            if len(self.data_log) > 100:
                self.data_log = self.data_log[-100:]
    
    def get_state(self) -> Dict[str, Any]:
        """
        温度センサーの現在の状態を取得する
        
        Returns:
            Dict[str, Any]: 温度センサーの状態
        """
        self._simulate_sensor_readings()
        return self.state
    
    def get_log(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        温度センサーのログデータを取得する
        
        Args:
            limit: 取得するログエントリの最大数
            
        Returns:
            List[Dict[str, Any]]: ログデータ
        """
        return self.data_log[-limit:]


class GameController(AccessoryDevice):
    """
    ゲームコントローラアクセサリ
    
    このクラスは、ゲームコントローラアクセサリをシミュレートします。
    ボタン、ジョイスティック、加速度センサー、振動機能などを備えています。
    """
    
    def __init__(self):
        """ゲームコントローラの初期化"""
        super().__init__(
            device_id="game_controller_001",
            name="Game Controller",
            manufacturer="ADK Tutorial",
            description="Game controller for Android devices",
            version="1.0",
            uri="https://example.com/adk/gamepad",
            serial_number="GAME00123456789",
            connection_type=ConnectionType.USB,
            protocol_version=ProtocolVersion.AOAv2
        )
        
        self.features = ["buttons", "joystick", "accelerometer", "vibration"]
        
        self.state = {
            "buttons": {
                "a": False,
                "b": False,
                "x": False,
                "y": False,
                "l1": False,
                "r1": False,
                "l2": 0.0,  # アナログトリガー（0.0-1.0）
                "r2": 0.0,  # アナログトリガー（0.0-1.0）
                "select": False,
                "start": False
            },
            "joystick": {
                "left": {"x": 0.0, "y": 0.0},  # -1.0から1.0の範囲
                "right": {"x": 0.0, "y": 0.0}  # -1.0から1.0の範囲
            },
            "accelerometer": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "vibration": {
                "left": 0.0,  # 0.0-1.0
                "right": 0.0  # 0.0-1.0
            }
        }
        
        logger.info("ゲームコントローラが初期化されました")
    
    def send_command(self, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        ゲームコントローラにコマンドを送信する
        
        Args:
            command: 送信するコマンド（set_vibration, read_input）
            params: コマンドのパラメータ
            
        Returns:
            Dict[str, Any]: コマンドの応答
        """
        if not self.connected:
            return {"status": "error", "message": "デバイスが接続されていません"}
        
        params = params.copy()
            
        response = {"status": "success", "data": {}}
        
        if command == "set_vibration":
            if "left" in params and 0 <= params["left"] <= 1:
                self.state["vibration"]["left"] = params["left"]
            
            if "right" in params and 0 <= params["right"] <= 1:
                self.state["vibration"]["right"] = params["right"]
                
            logger.info(f"振動を設定しました: 左={self.state['vibration']['left']}, 右={self.state['vibration']['right']}")
            response["data"]["vibration"] = self.state["vibration"]
                
        elif command == "read_input":
            self._simulate_input()
            logger.info("入力状態を読み取りました")
            response["data"] = self.state
                
        else:
            response = {"status": "error", "message": f"未知のコマンド: {command}"}
            
        return response
    
    def _simulate_input(self):
        """コントローラの入力をシミュレートする"""
        for button in self.state["buttons"]:
            if isinstance(self.state["buttons"][button], bool):
                self.state["buttons"][button] = random.random() < 0.1  # 10%の確率で押下
            else:
                self.state["buttons"][button] = random.random() * 0.3  # 0.0-0.3のランダムな値
        
        for stick in ["left", "right"]:
            self.state["joystick"][stick]["x"] = random.uniform(-0.2, 0.2)
            self.state["joystick"][stick]["y"] = random.uniform(-0.2, 0.2)
        
        self.state["accelerometer"]["x"] = random.uniform(-0.5, 0.5)
        self.state["accelerometer"]["y"] = random.uniform(-0.5, 0.5)
        self.state["accelerometer"]["z"] = random.uniform(0.8, 1.0)  # 重力方向
    
    def get_state(self) -> Dict[str, Any]:
        """
        ゲームコントローラの現在の状態を取得する
        
        Returns:
            Dict[str, Any]: ゲームコントローラの状態
        """
        return self.state



class ADKManager:
    """
    ADKデバイスを管理するクラス
    
    このクラスは、複数のADKアクセサリデバイスを管理し、それらとの通信を
    簡素化するためのインターフェースを提供します。
    """
    
    def __init__(self):
        """ADKマネージャーの初期化"""
        self.devices = {}
        logger.info("ADKマネージャーが初期化されました")
    
    def register_device(self, device: AccessoryDevice) -> bool:
        """
        新しいアクセサリデバイスを登録する
        
        Args:
            device: 登録するAccessoryDeviceオブジェクト
            
        Returns:
            bool: 登録が成功したかどうか
        """
        if device.device_id in self.devices:
            logger.warning(f"デバイスID '{device.device_id}' は既に登録されています")
            return False
        
        self.devices[device.device_id] = device
        logger.info(f"デバイス '{device.name}' (ID: {device.device_id}) が登録されました")
        return True
    
    def unregister_device(self, device_id: str) -> bool:
        """
        アクセサリデバイスの登録を解除する
        
        Args:
            device_id: 登録解除するデバイスのID
            
        Returns:
            bool: 登録解除が成功したかどうか
        """
        if device_id not in self.devices:
            logger.warning(f"デバイスID '{device_id}' は登録されていません")
            return False
        
        if self.devices[device_id].connected:
            self.devices[device_id].disconnect()
        
        device_name = self.devices[device_id].name
        del self.devices[device_id]
        logger.info(f"デバイス '{device_name}' (ID: {device_id}) の登録が解除されました")
        return True
    
    def get_device(self, device_id: str) -> Optional[AccessoryDevice]:
        """
        指定されたIDのデバイスを取得する
        
        Args:
            device_id: 取得するデバイスのID
            
        Returns:
            Optional[AccessoryDevice]: デバイスオブジェクト（存在しない場合はNone）
        """
        if device_id not in self.devices:
            logger.warning(f"デバイスID '{device_id}' は登録されていません")
            return None
        
        return self.devices[device_id]
    
    def get_all_devices(self) -> Dict[str, AccessoryDevice]:
        """
        登録されているすべてのデバイスを取得する
        
        Returns:
            Dict[str, AccessoryDevice]: デバイスIDをキーとするデバイスオブジェクトの辞書
        """
        return self.devices
    
    def connect_device(self, device_id: str) -> bool:
        """
        指定されたデバイスを接続する
        
        Args:
            device_id: 接続するデバイスのID
            
        Returns:
            bool: 接続が成功したかどうか
        """
        device = self.get_device(device_id)
        if device is None:
            return False
        
        return device.connect()
    
    def disconnect_device(self, device_id: str) -> bool:
        """
        指定されたデバイスを切断する
        
        Args:
            device_id: 切断するデバイスのID
            
        Returns:
            bool: 切断が成功したかどうか
        """
        device = self.get_device(device_id)
        if device is None:
            return False
        
        return device.disconnect()
    
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        指定されたデバイスにコマンドを送信する
        
        Args:
            device_id: コマンドを送信するデバイスのID
            command: 送信するコマンド
            params: コマンドのパラメータ
            
        Returns:
            Dict[str, Any]: コマンドの応答
        """
        device = self.get_device(device_id)
        if device is None:
            return {"status": "error", "message": f"デバイスID '{device_id}' は登録されていません"}
        
        params = params.copy()
        return device.send_command(command, params)



def run_led_controller_demo():
    """
    LEDコントローラのデモを実行する
    
    このデモでは、LEDコントローラの接続、明るさ・色・パターンの設定、切断の一連の流れを示します。
    """
    print("\n" + "="*80)
    print("LEDコントローラデモ")
    print("="*80)
    
    manager = ADKManager()
    
    led_controller = LEDController()
    manager.register_device(led_controller)
    
    device_info = led_controller.get_info()
    print(f"\nデバイス情報:")
    print(f"  名前: {device_info['name']}")
    print(f"  製造元: {device_info['manufacturer']}")
    print(f"  説明: {device_info['description']}")
    print(f"  接続タイプ: {device_info['connection_type']}")
    print(f"  プロトコル: {device_info['protocol_version']}")
    print(f"  機能: {', '.join(device_info['features'])}")
    
    print("\nLEDコントローラを接続しています...")
    manager.connect_device(led_controller.device_id)
    
    print("\n明るさを75%に設定しています...")
    response = manager.send_command(led_controller.device_id, "set_brightness", {"value": 75})
    print(f"応答: {response}")
    
    print("\n色を赤(#FF0000)に設定しています...")
    response = manager.send_command(led_controller.device_id, "set_color", {"value": "#FF0000"})
    print(f"応答: {response}")
    
    print("\nパターンをpulseに設定しています...")
    response = manager.send_command(led_controller.device_id, "set_pattern", {"value": "pulse"})
    print(f"応答: {response}")
    
    print("\n電源をオンにしています...")
    response = manager.send_command(led_controller.device_id, "power", {"value": True})
    print(f"応答: {response}")
    
    state = led_controller.get_state()
    print("\n現在のLEDコントローラの状態:")
    print(f"  明るさ: {state['brightness']}%")
    print(f"  色: {state['color']}")
    print(f"  パターン: {state['pattern']}")
    print(f"  電源: {'オン' if state['power'] else 'オフ'}")
    
    print("\nLEDコントローラを切断しています...")
    manager.disconnect_device(led_controller.device_id)
    
    print("\nLEDコントローラデモが完了しました")


def run_temperature_sensor_demo():
    """
    温度センサーのデモを実行する
    
    このデモでは、温度センサーの接続、温度・湿度の読み取り、データログの取得、切断の一連の流れを示します。
    """
    print("\n" + "="*80)
    print("温度センサーデモ")
    print("="*80)
    
    manager = ADKManager()
    
    temp_sensor = TemperatureSensor()
    manager.register_device(temp_sensor)
    
    device_info = temp_sensor.get_info()
    print(f"\nデバイス情報:")
    print(f"  名前: {device_info['name']}")
    print(f"  製造元: {device_info['manufacturer']}")
    print(f"  説明: {device_info['description']}")
    print(f"  接続タイプ: {device_info['connection_type']}")
    print(f"  プロトコル: {device_info['protocol_version']}")
    print(f"  機能: {', '.join(device_info['features'])}")
    
    print("\n温度センサーを接続しています...")
    manager.connect_device(temp_sensor.device_id)
    
    print("\n温度を読み取っています...")
    response = manager.send_command(temp_sensor.device_id, "read_temperature")
    print(f"応答: {response}")
    print(f"現在の温度: {response['data']['temperature']}°C")
    
    print("\n湿度を読み取っています...")
    response = manager.send_command(temp_sensor.device_id, "read_humidity")
    print(f"応答: {response}")
    print(f"現在の湿度: {response['data']['humidity']}%")
    
    print("\nデータログを開始しています...")
    response = manager.send_command(temp_sensor.device_id, "start_logging", {"interval": 5})
    print(f"応答: {response}")
    
    print("\nデータを収集しています...")
    for i in range(5):
        print(f"  測定 {i+1}/5...")
        time.sleep(1)
        temp_sensor._simulate_sensor_readings()
    
    print("\nデータログを停止しています...")
    response = manager.send_command(temp_sensor.device_id, "stop_logging")
    print(f"応答: {response}")
    
    log_data = temp_sensor.get_log()
    print("\nログデータ:")
    for entry in log_data:
        timestamp = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
        print(f"  {timestamp} - 温度: {entry['temperature']}°C, 湿度: {entry['humidity']}%")
    
    print("\n温度センサーを切断しています...")
    manager.disconnect_device(temp_sensor.device_id)
    
    print("\n温度センサーデモが完了しました")


def run_game_controller_demo():
    """
    ゲームコントローラのデモを実行する
    
    このデモでは、ゲームコントローラの接続、入力の読み取り、振動の設定、切断の一連の流れを示します。
    """
    print("\n" + "="*80)
    print("ゲームコントローラデモ")
    print("="*80)
    
    manager = ADKManager()
    
    game_controller = GameController()
    manager.register_device(game_controller)
    
    device_info = game_controller.get_info()
    print(f"\nデバイス情報:")
    print(f"  名前: {device_info['name']}")
    print(f"  製造元: {device_info['manufacturer']}")
    print(f"  説明: {device_info['description']}")
    print(f"  接続タイプ: {device_info['connection_type']}")
    print(f"  プロトコル: {device_info['protocol_version']}")
    print(f"  機能: {', '.join(device_info['features'])}")
    
    print("\nゲームコントローラを接続しています...")
    manager.connect_device(game_controller.device_id)
    
    print("\n入力状態を読み取っています...")
    response = manager.send_command(game_controller.device_id, "read_input")
    print(f"応答: {response}")
    
    input_state = response["data"]
    print("\n現在の入力状態:")
    
    print("  ボタン:")
    for button, state in input_state["buttons"].items():
        if isinstance(state, bool):
            print(f"    {button}: {'押されている' if state else '押されていない'}")
        else:
            print(f"    {button}: {state:.2f}")
    
    print("  ジョイスティック:")
    for stick, axes in input_state["joystick"].items():
        print(f"    {stick}: X={axes['x']:.2f}, Y={axes['y']:.2f}")
    
    print("  加速度センサー:")
    accel = input_state["accelerometer"]
    print(f"    X={accel['x']:.2f}, Y={accel['y']:.2f}, Z={accel['z']:.2f}")
    
    print("\n振動を設定しています...")
    response = manager.send_command(game_controller.device_id, "set_vibration", {"left": 0.8, "right": 0.5})
    print(f"応答: {response}")
    print(f"振動設定: 左={response['data']['vibration']['left']}, 右={response['data']['vibration']['right']}")
    
    print("\nゲームコントローラを切断しています...")
    manager.disconnect_device(game_controller.device_id)
    
    print("\nゲームコントローラデモが完了しました")


def run_all_demos():
    """すべてのデモを順番に実行する"""
    print("\n" + "="*80)
    print("Android Accessory Development Kit (ADK) チュートリアル")
    print("="*80)
    print("\nこのチュートリアルでは、ADKを使用してAndroidデバイスと外部アクセサリを接続する方法を示します。")
    print("以下の3つのデモを順番に実行します:")
    print("  1. LEDコントローラ - 明るさ、色、パターンの制御")
    print("  2. 温度センサー - 温度、湿度の読み取りとデータログ")
    print("  3. ゲームコントローラ - 入力の読み取りと振動の制御")
    
    input("\nEnterキーを押して開始...")
    
    run_led_controller_demo()
    input("\nEnterキーを押して次のデモに進む...")
    
    run_temperature_sensor_demo()
    input("\nEnterキーを押して次のデモに進む...")
    
    run_game_controller_demo()
    
    print("\n" + "="*80)
    print("すべてのデモが完了しました")
    print("="*80)
    print("\nこのチュートリアルでは、ADKの基本的な使い方を示しました。")
    print("実際のハードウェアでは、USBまたはBluetoothを介してAndroidデバイスと通信します。")
    print("詳細については、ドキュメントを参照してください。")



def main():
    """メイン関数"""
    import argparse
    parser = argparse.ArgumentParser(description="Android Accessory Development Kit (ADK) チュートリアル")
    parser.add_argument("--demo", choices=["led", "temp", "game", "all"], default="all",
                        help="実行するデモ（led: LEDコントローラ, temp: 温度センサー, game: ゲームコントローラ, all: すべて）")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細なログを表示する")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.demo == "led":
        run_led_controller_demo()
    elif args.demo == "temp":
        run_temperature_sensor_demo()
    elif args.demo == "game":
        run_game_controller_demo()
    else:  # all
        run_all_demos()


if __name__ == "__main__":
    main()
