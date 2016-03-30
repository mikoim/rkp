<?php
/* 必要なパラメータに含まれているか確認 */
if(!isset($_GET['year']) || !isset($_GET['season']) || !isset($_GET['department']) || !isset($_GET['keyword']) || !isset($_GET['page'])) {
    exit();
}

$reverse = -1;
$year = intval($_GET['year']);
$poge = intval($_GET['page']);
$season = null;
switch($_GET['season']) {
    case "ALL":
        break;
    case "spring":
        $season = "春";
        break;
    case "autumn":
        $season = "秋";
        break;
    default:
        exit();
}
$query = array();

if(isset($_GET['SortReverse'])) $reverse = 1;

/* キーワードを分割 */
$target = Normalizer::normalize((string)$_GET['keyword'], Normalizer::FORM_KC);

if ($target != null) {
    $temp = explode(' ', $target);

    foreach ($temp as $value) {
        array_push($query, new MongoRegex('/' . $value . "/i"));
    }
}

/* データベースに接続 */
$m = new MongoClient();
$db = $m->drl;
$collection = $db->lecture;

/* 条件式を生成 */
$condArray = array(
    array('登録者数' => array('$gt' => 0)),
    array('評点平均値' => array('$gt' => 0))
);

if($_GET['department'] != 'ALL') array_push($condArray, array('dId' => (string)$_GET['department']));
if($year >= 2004 && $year <= 2013) array_push($condArray, array('年度' => $year));
if($season != null) array_push($condArray, array('開講期間' => $season));
if($query) {
    $search = array();

    foreach($query as $value) {
        array_push($search, array('searchText' => $value));
    }

    array_push($condArray, array('$and' => $search));
}

/* データを取得 */
$cursor = $collection->find(
    array('$and' => $condArray),
    array('searchText' => false, 'RKP' => false, '_id' => false, 'dId' => false, '課程' => false, '備考' => false)
);

$count = $cursor->count();

if(isset($_GET['SortRKP'])) {
    $cursor->sort(array('RKP' => $reverse, '年度' => -1));
} else {
    $cursor->sort(array('評点平均値' => $reverse, '年度' => -1));
}
if(50 * ($poge - 1) > 0) $cursor->skip(50 * ($poge - 1));
$cursor->limit(50);

$result = iterator_to_array($cursor);
$info = array('total' => $count, 'limit' => 50);

echo json_encode(array('info' => $info, 'data' => $result));