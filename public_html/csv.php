<html>
<head>
<link rel="stylesheet" type="text/css" href="./styled-table.css" media="screen"/>
<link rel="stylesheet" type="text/css" href="./body.css" media="screen"/>
</head>
<body>
<div>
<h2>**Unofficial** Digg Rebase History</h2>
<p>For the official app, please visit <a href="https://app.badger.finance/digg">app.badger.finance/digg</a>.</p>
<p>See below for a very simple table of the digg rebase history</p>
<?php
echo "<table class=\"styled-table\">\n\n";
$f = fopen("rebase.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table>\n";
?>
<p>If you want to download the csv of this data, feel free:<br>
<a href="./rebase.csv">rebase.csv</a>
</p>
<BR>
</div>
</body>
</html>
