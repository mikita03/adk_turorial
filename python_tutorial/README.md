# Android Accessory Development Kit (ADK) チュートリアル

このチュートリアルでは、Android Accessory Development Kit (ADK) の基本的な使い方を Python で実装したシミュレーションを通じて学びます。ADK を使用すると、Android デバイスと外部ハードウェアアクセサリを接続し、通信することができます。

## 目次

1. [ADK の概要](#adk-の概要)
2. [チュートリアルの構成](#チュートリアルの構成)
3. [使用方法](#使用方法)
4. [コンポーネントの説明](#コンポーネントの説明)
   - [AccessoryDevice](#accessorydevice)
   - [LEDController](#ledcontroller)
   - [TemperatureSensor](#temperaturesensor)
   - [GameController](#gamecontroller)
   - [ADKManager](#adkmanager)
5. [デモの実行](#デモの実行)
6. [コード例](#コード例)
7. [参考リソース](#参考リソース)

## ADK の概要

Android Accessory Development Kit (ADK) は、Android デバイスと外部ハードウェアアクセサリを接続するためのリファレンス実装です。ADK は Android Open Accessory (AOA) プロトコルに基づいており、Android デバイスが「アクセサリモード」で動作することを可能にします。

### 主な特徴

- **USB アクセサリモード**: アクセサリが USB ホストとして機能し、Android デバイスと通信します
- **AOA プロトコル**: Android デバイスとアクセサリ間の標準化された通信プロトコル（AOAv1 と AOAv2）
- **ハードウェア統合**: センサー、コントローラ、ディスプレイなどの様々なハードウェアとの統合
- **Android API サポート**: アクセサリの検出、接続、通信のための Android アプリケーション API

### ADK の仕組み

1. **アクセサリ検出**: Android デバイスが USB 経由でアクセサリに接続されると、アクセサリはベンダー固有の USB コントロールリクエストを使用して Android Open Accessory として自身を識別します
2. **プロトコルネゴシエーション**: アクセサリと Android デバイスが使用する AOA プロトコルのバージョンをネゴシエートします
3. **アクセサリモードの有効化**: Android デバイスがアクセサリモードに入り、アクセサリが USB ホストになります
4. **通信**: Android アプリケーションとアクセサリが USB 経由でバルク転送を使用して通信します

## チュートリアルの構成

このチュートリアルは、ADK の基本的な概念と使用方法を示すために、以下のコンポーネントで構成されています：

- **基本クラス**: `AccessoryDevice` - すべてのアクセサリデバイスの基本クラス
- **デバイスシミュレーション**:
  - `LEDController` - LED の明るさ、色、パターンを制御するアクセサリ
  - `TemperatureSensor` - 温度と湿度を測定するセンサーアクセサリ
  - `GameController` - ボタン、ジョイスティック、加速度センサーを持つゲームコントローラアクセサリ
- **管理クラス**: `ADKManager` - アクセサリデバイスの登録、接続、通信を管理
- **デモ関数**: 各アクセサリタイプのデモンストレーション

## 使用方法

### 必要条件

- Python 3.6 以上
- 標準ライブラリのみを使用（外部依存関係なし）

### インストール

このチュートリアルは外部依存関係を持たないため、リポジトリをクローンするだけで使用できます：

```bash
git clone https://github.com/yourusername/adk_tutorial.git
cd adk_tutorial/python_tutorial
```

### 実行方法

すべてのデモを実行するには：

```bash
python src/adk_tutorial.py
```

特定のデモのみを実行するには：

```bash
# LEDコントローラデモ
python src/adk_tutorial.py --demo led

# 温度センサーデモ
python src/adk_tutorial.py --demo temp

# ゲームコントローラデモ
python src/adk_tutorial.py --demo game
```

詳細なログを表示するには：

```bash
python src/adk_tutorial.py --verbose
```

## コンポーネントの説明

### AccessoryDevice

`AccessoryDevice` は、すべてのアクセサリデバイスの基本クラスです。このクラスは、アクセサリの基本的な属性と機能を定義します：

- **属性**:
  - `device_id`: デバイスの一意の識別子
  - `name`: デバイスの名前
  - `manufacturer`: 製造元
  - `description`: デバイスの説明
  - `connection_type`: 接続タイプ（USB または Bluetooth）
  - `protocol_version`: AOA プロトコルのバージョン（AOAv1 または AOAv2）
  - `features`: デバイスの機能リスト
  - `connected`: 接続状態

- **メソッド**:
  - `connect()`: デバイスを接続する
  - `disconnect()`: デバイスを切断する
  - `send_command(command, params)`: デバイスにコマンドを送信する
  - `get_info()`: デバイス情報を取得する

### LEDController

`LEDController` は、LED の明るさ、色、パターンを制御するアクセサリをシミュレートします：

- **状態**:
  - `brightness`: LED の明るさ（0-100%）
  - `color`: LED の色（16進数カラーコード）
  - `pattern`: LED のパターン（solid, blink, pulse, rainbow）
  - `power`: 電源状態（オン/オフ）

- **コマンド**:
  - `set_brightness`: LED の明るさを設定する
  - `set_color`: LED の色を設定する
  - `set_pattern`: LED のパターンを設定する
  - `power`: LED の電源をオン/オフする

### TemperatureSensor

`TemperatureSensor` は、温度と湿度を測定するセンサーアクセサリをシミュレートします：

- **状態**:
  - `temperature`: 現在の温度（摂氏）
  - `humidity`: 現在の湿度（%）
  - `logging`: データログの状態（オン/オフ）
  - `log_interval`: ログの間隔（秒）
  - `data_log`: 記録されたデータのリスト

- **コマンド**:
  - `read_temperature`: 現在の温度を読み取る
  - `read_humidity`: 現在の湿度を読み取る
  - `start_logging`: データログを開始する
  - `stop_logging`: データログを停止する

### GameController

`GameController` は、ボタン、ジョイスティック、加速度センサーを持つゲームコントローラアクセサリをシミュレートします：

- **状態**:
  - `buttons`: ボタンの状態（A, B, X, Y, L, R, Start, Select）
  - `joystick`: ジョイスティックの位置（left, right）
  - `accelerometer`: 加速度センサーの値（x, y, z）
  - `vibration`: 振動モーターの強度（left, right）

- **コマンド**:
  - `read_input`: 現在の入力状態を読み取る
  - `set_vibration`: 振動モーターの強度を設定する

### ADKManager

`ADKManager` は、アクセサリデバイスの登録、接続、通信を管理するクラスです：

- **メソッド**:
  - `register_device(device)`: デバイスを登録する
  - `unregister_device(device_id)`: デバイスの登録を解除する
  - `get_device(device_id)`: デバイスを取得する
  - `get_all_devices()`: すべての登録済みデバイスを取得する
  - `connect_device(device_id)`: デバイスを接続する
  - `disconnect_device(device_id)`: デバイスを切断する
  - `send_command(device_id, command, params)`: デバイスにコマンドを送信する

## デモの実行

このチュートリアルには、3つのデモが含まれています：

### LEDコントローラデモ

LEDコントローラデモでは、以下の操作を行います：

1. LEDコントローラの登録と接続
2. 明るさを75%に設定
3. 色を赤(#FF0000)に設定
4. パターンをpulseに設定
5. 電源をオンにする
6. 現在の状態を表示
7. LEDコントローラを切断

### 温度センサーデモ

温度センサーデモでは、以下の操作を行います：

1. 温度センサーの登録と接続
2. 現在の温度を読み取る
3. 現在の湿度を読み取る
4. データログを開始する
5. 5回のデータ測定を行う
6. データログを停止する
7. ログデータを表示
8. 温度センサーを切断

### ゲームコントローラデモ

ゲームコントローラデモでは、以下の操作を行います：

1. ゲームコントローラの登録と接続
2. 現在の入力状態を読み取る
3. ボタン、ジョイスティック、加速度センサーの状態を表示
4. 振動を設定する
5. ゲームコントローラを切断

## コード例

### アクセサリデバイスの作成と接続

```python
# ADKManagerの作成
manager = ADKManager()

# LEDコントローラの作成と登録
led_controller = LEDController()
manager.register_device(led_controller)

# LEDコントローラを接続
manager.connect_device(led_controller.device_id)

# LEDコントローラにコマンドを送信
response = manager.send_command(led_controller.device_id, "set_brightness", {"value": 75})
print(f"応答: {response}")

# LEDコントローラを切断
manager.disconnect_device(led_controller.device_id)
```

### 独自のアクセサリデバイスの作成

```python
class MyCustomAccessory(AccessoryDevice):
    def __init__(self):
        super().__init__(
            name="My Custom Accessory",
            manufacturer="My Company",
            description="A custom accessory for demonstration",
            connection_type=ConnectionType.USB,
            protocol_version=ProtocolVersion.AOAv2,
            features=["feature1", "feature2"]
        )
        
        # デバイス固有の状態
        self.state = {
            "parameter1": 0,
            "parameter2": "default"
        }
    
    def send_command(self, command: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        params = params.copy()
        
        if not self.connected:
            return {"status": "error", "message": "デバイスが接続されていません"}
        
        response = {"status": "success", "data": {}}
        
        if command == "set_parameter1":
            if "value" in params:
                self.state["parameter1"] = params["value"]
                response["data"]["parameter1"] = self.state["parameter1"]
            else:
                response = {"status": "error", "message": "valueパラメータが必要です"}
        
        elif command == "set_parameter2":
            if "value" in params:
                self.state["parameter2"] = params["value"]
                response["data"]["parameter2"] = self.state["parameter2"]
            else:
                response = {"status": "error", "message": "valueパラメータが必要です"}
        
        else:
            response = {"status": "error", "message": f"不明なコマンド: {command}"}
        
        return response
```

## 参考リソース

- [Android Developers - USB Accessory](https://developer.android.com/develop/connectivity/usb/accessory)
- [Android Open Accessory Protocol](https://source.android.com/devices/accessories/aoa)
- [ADK 2012 Guide](https://source.android.com/devices/accessories/adk2)
