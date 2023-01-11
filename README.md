# auto-nsfw-checker
## これはなに？

Mastodonのローカルタイムラインを監視し、「NSFWが付いていないNSFWな画像」を投稿されていないかをチェックするBotです。

## 使用したライブラリなど

Mastodonのローカルタイムライン監視
[halcy/Mastodon.py](https://github.com/halcy/Mastodon.py)

画像がNSFWかどうかの判定モデル
[bhky/opennsfw2](https://github.com/bhky/opennsfw2)

