import polars as pl
import utils

file_path ='api_gpt4o.json'                   # API接続情報のファイルパス
api_data = utils.load_api_data(file_path)     # API接続情報を取得
client, model = utils.create_client(api_data) # AzureOpenAIクライアント、モデル名を取得

# Excelデータの読み込み
df_shain  = pl.read_excel('test社員マスタ.xlsx',sheet_name='Sheet1')
df_shohin = pl.read_excel('test商品マスタ.xlsx',sheet_name='Sheet1')
df_hanbai = pl.read_excel('test販売実績.xlsx'  ,sheet_name='Sheet1',read_options={"header_row": 2})

# 結合
df_all = df_hanbai.join(df_shain,on='社員番号',how='left')  #販売実績に社員ﾏｽﾀを結合
df_all = df_all.join(df_shohin,on='商品番号',how='left')    #販売実績に商品ﾏｽﾀを結合

#金額を計算
df_all = df_all.with_columns( (pl.col('数量') * pl.col('単価')).alias('金額'))
print(df_all)

#ピボット集計
df_pivot = df_all.pivot(index='商品名',on='氏名',values='金額',aggregate_function="sum")
print(df_pivot)

   

# 商品ごとに備考をまとめる
df_bikou = df_all.group_by(['商品名']).agg(pl.col('備考').alias('備考list'))   # group_by で集計し、商品名,備考list のテーブルを作成 
df_bikou = df_bikou.with_columns(pl.lit('').alias('備考str'), pl.lit('').alias('改善点')) # 空のカラムを追加し、商品名,備考欄list,備考str,改善点 とする
print(df_bikou  )

# AIへの指示文 を作成
content = """\n\n
上記の文章から売上増加させるポイントを３つほど箇条書きで示して。
箇条書きは行頭に(1),(2),(3)をつけ、完結に記載すること。
該当箇所がない場合は「ない」とだけ回答すること。
"""


# AIで商品ごとに備考から改善点を抽出する。
for i in range(len(df_bikou)):
    print(f'要約中 : {i+1}/{len(df_bikou)}')
    df_bikou[i, '備考str'] = ''.join('・' + df_bikou[i, '備考list'] + '\n')    # 備考listはlist(str)型 のため 備考str(str型)へ変換する。 
    prompt = df_bikou[i, '備考str'] + content                                  # 備考strに指示文をつけて、プロンプトとする。
    df_bikou[i, '改善点'] = utils.get_response(client, model, prompt)          # AIにプロンプトを投げ、レスポンスとして得られた改善点を保存  

# 商品ごとの改善点を ピボット集計結果に結合する。
df_bikou = df_bikou.select('商品名', '備考str', '改善点')     # テーブルから商品名、備考str、改善点を選択 （備考欄listの列を削除） 
df_pivot = df_pivot.join(df_bikou, on='商品名', how='left')  # 集計結果の df_pivot に 改善点 df_bikou を結合する。

df_pivot.write_excel('df_pivot')
print('処理終了')
