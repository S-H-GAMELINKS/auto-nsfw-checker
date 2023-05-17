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
        print(e)

# 連合タイムラインをListenするためのクラスを定義
class PublicStreamListener(StreamListener):

    # 引数に生成したMastodonのクライアントが必須
    def __init__(self, client):
        super(PublicStreamListener, self).__init__()
        self.client = client

    def handle_stream(self, response):
        try:
            super().handle_stream(response)
        except:
            print(response)
            print("Error!")

    def on_update(self, status):
        # 投稿の画像データとNSFWフラグを取得
        media_attachments = status.get('media_attachments')

        # 画像をチェック
        if len(media_attachments) > 0:
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

                # 基準値以上の場合は通報
                if result > 0.90:
                    # 投稿のIDとアカウントを取得
                    statusID = status.id
                    account = status.account

                    # ログにアカウント情報などを出力
                    print(account.id)
                    print(self.client.account_followers(account.id))

                    # 通報対象の投稿をしたアカウントをフォローしているユーザーがいるかを取得
                    target_account_followers = self.client.account_followers(account.id)

                    # 通報を行い、該当の投稿を自動削除
                    # 条件：対象の投稿をしたアカウントをフォローしているユーザーがサーバ内にいない
                    if len(target_account_followers) == 0:
                        self.client.report(account.id, status_ids=[statusID])
                        self.client.status_delete(statusID)

                    break

# 連合タイムラインのListenerを生成            
public_stream_listener = PublicStreamListener(client)

# 連合タイムラインをListen
client.stream_public(public_stream_listener, remote=True)
