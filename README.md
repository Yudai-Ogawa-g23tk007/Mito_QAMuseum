# 量子アニーリングを利用した美術館の巡回経路最適化アプリケーション
## 1.本プロジェクトについて
本プロジェクトは, スマートフォンで利用可能な美術館の巡回経路最適化Webアプリケーションを開発し, 量子技術関係者や研究者ではない一般の方にも量子コンピューティング技術に触れてもらう機会の創出を目指したものである.
2023年度未踏ターゲット事業内で開発したアプリケーションのソースコードについて，一般に利用してもらうことを目的として公開を行う．
本プロジェクトは2023年度未踏ターゲット事業の支援を受けている．

## 2.用意するデータ
本ソースコードの利用には次の美術館データを用意する必要がある．
* 美術館の展示数
* 美術館の展示情報（名前，説明，写真，閲覧時間，満足度,展示間の移動時間）
* 美術館の展示の配置
* 美術館の館内図・配置図

また，別途Amplify社のサイト (https://amplify.fixstars.com/ja/) からアニーリングマシンの利用のためのアクセストークンを取得する必要がある．

## 3.アプリケーションの構成
本項では，本アプリケーションの構成について説明する．

**フレームワーク**　:　Django

**言語**　:　Python,HTML,CSS,javascript

**ライブラリ**　:　Amplify SDK,NumPy,PIL,Matplotlib,Django-widget-tweaks

**データベース**　:　SQlite,Redis

## 4.アプリケーションの起動
本ソースコードを利用する場合，構成を設定後コードを変更しプログラムを次の手順に従ってプログラムを実行してください．
まず，Redisサーバーを起動して，非同期処理用にceleryを起動してください．
```
redis-server
cd STSP
celery -A STSP worker -l INFO 
```
次に`manage.py`の存在するディレクトリからサーバーを起動してください．
```
python manage.py runserver
```


