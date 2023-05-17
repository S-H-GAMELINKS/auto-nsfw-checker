from mastodon import Mastodon, StreamListener
import opennsfw2 as n2
from dotenv import load_dotenv
import os
import pprint
import time
import urllib.error
import urllib.request

# .envの読み込み
load_dotenv()

# Mastodonのクライアント生成
client = Mastodon(api_base_url = os.environ['API_BASE_URL'], access_token = os.environ['ACCESS_TOKEN'])

# 画像を一旦保存するための処理
# opennsfw2ではファイルパスで画像を渡す必要があるため
def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        pass

# ローカルタイムラインをListenするためのクラスを定義
class LocalStreamListener(StreamListener):

    # 引数に生成したMastodonのクライアントが必須
    def __init__(self, client):
        super(LocalStreamListener, self).__init__()
        self.client = client

    def handle_stream(self, response):
        try:
            super().handle_stream(response)
        except:
            pass

    def on_update(self, status):
        try:
            # 投稿の画像データとNSFWフラグを取得
            sensitive = status.get('sensitive')
            media_attachments = status.get('media_attachments')

            # NSFWフラグが無効になっている画像をチェック
            if sensitive == False and len(media_attachments) > 0:
                for media_attachment in media_attachments:
                    # ログに画像のURLを出力
                    print(media_attachment.url)

                    # 画像を一時的に保存
                    dst_path = './nsfw'
                    download_file(media_attachment.url, dst_path)

                    # 画像がNSFWなものかをチェックし、ダウンロードした画像は削除
                    result = n2.predict_image(dst_path)
                    os.remove(dst_path)

                    # チェック結果をログに出力
                    print(result)

                    # 基準値以上の場合はリプライで警告しつつ、通報を追加
                    if result > 0.90:
                        self.client.report(status.account.id, status_ids=[status.id])
                        self.client.status_reply(status, 'NSFWな画像です。投稿を編集してNSFWを有効にしてください', status.id)
                        break
        except Exception as e:
            print(e)
            pass

# ローカルタイムラインのListenerを生成            
stream_listener = LocalStreamListener(client)

# ローカルタイムラインをListen
client.stream_local(stream_listener)
