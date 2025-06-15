import utils

file_path ='api_gpt4o.json'                   # API接続情報のファイルパス
api_data = utils.load_api_data(file_path)     # API接続情報を取得
client, model = utils.create_client(api_data) # AzureOpenAIクライアント、モデル名を取得

content = "10割る3を計算してください"           # プロンプトを作成
response = utils.get_response(client, model, content)  # チャットを実行

print(response)  # チャットの結果を表示
