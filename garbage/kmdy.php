<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="弁当チェーン「本家かまどや」のコスパランキング">
    <meta name="keywords" content="同志社大学,講義,評価,楽勝科目,楽勝般教,弁当,コスパランキング,本家かまどや,ほっともっと">
    <title>RKP - 「本家かまどや」 コスパランキング</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
    <link href="css/a.css" rel="stylesheet">
    <link rel="shortcut icon" href="img/favicon.png">
</head>
<body>
<nav class="navbar navbar-default navbar-static-top" role="navigation">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">RKP r2</a>
        </div>
        <div class="navbar-collapse collapse">
            <ul class="nav navbar-nav">
                <li><a href="kmdy.php">本家かまどや</a></li>
                <li><a href="homo.php">ほっともっと</a></li>
            </ul>
        </div>
    </div>
</nav>
<div class="container-fluid">
    <div class="panel panel-default">
        <div class="panel-heading">「本家かまどや」 コスパランキング</div>
        <div class="panel-body">
            <p>2014/06/09 (月) : 最新の情報にアップデートしました.</p>
        </div>
        <div class="table-responsive">
            <table class="table table-condensed table-hover table-striped">
                <thead>
                <tr>
                    <th>#</th>
                    <th>名前</th>
                    <th>値段</th>
                    <th>エネルギー</th>
                    <th>蛋白質</th>
                    <th>脂質</th>
                    <th>炭水化物</th>
                    <th>食塩相当量</th>
                    <th>kcal/円</th>
                </tr>
                </thead>
                <tbody>
                <?php
                $m = new MongoClient();
                $db = $m->kmdy;

                $collection = $db->bento;

                $bentos = iterator_to_array($collection->find()->sort(array('kbs' => -1)));
                $i = 1;
                foreach ($bentos as $bento) {
                    printf('<tr><td>%d</td><td>%s</td><td>%d 円</td><td>%.2f kcal</td><td>%.2f g</td><td>%.2f g</td><td>%.2f g</td><td>%.2f g</td><td>%f kcal/円</td></tr>',
                        $i, $bento['name'], $bento['price'], $bento['label'][0], $bento['label'][1], $bento['label'][2], $bento['label'][3], $bento['label'][4], $bento['kbs']);
                    $i++;
                }

                ?>
                </tbody>
            </table>
        </div>
    </div>
    <div class="text-muted text-center">
        <p>Any questions? Please contact <a href="http://www.google.com/recaptcha/mailhide/d?k=01z9IDcoOstsPH4m__Mg2FVw==&amp;c=rWHp61aBaWsV7suWtN4edGefMaDcGQL5pTpTxcXl1jU=" onclick="window.open('http://www.google.com/recaptcha/mailhide/d?k\07501z9IDcoOstsPH4m__Mg2FVw\75\75\46c\75rWHp61aBaWsV7suWtN4edGefMaDcGQL5pTpTxcXl1jU\075', '', 'toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=0,width=500,height=300'); return false;" title="Reveal this e-mail address">me</a>.</p>
    </div>
</div>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
<script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
<script>
    (function (i, s, o, g, r, a, m) {
        i['GoogleAnalyticsObject'] = r;
        i[r] = i[r] || function () {
            (i[r].q = i[r].q || []).push(arguments)
        }, i[r].l = 1 * new Date();
        a = s.createElement(o),
            m = s.getElementsByTagName(o)[0];
        a.async = 1;
        a.src = g;
        m.parentNode.insertBefore(a, m)
    })(window, document, 'script', '//www.google-analytics.com/analytics.js', 'ga');
    ga('create', 'UA-44033957-7', 'ddo.jp');
    ga('require', 'displayfeatures');
    ga('require', 'linkid', 'linkid.js');
    ga('send', 'pageview');
</script>
</body>
</html>