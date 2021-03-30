<html>
<head>
<link rel="stylesheet" type="text/css" href="css/sortable.css" media="screen"/>
<link rel="stylesheet" type="text/css" href="./body.css" media="screen"/>
</head>
<body>
<div>
<h2>NFT diamond hands</h2>
<p>Data is polled from Etherscan every 15-20 minutes.</p>
<p>If you need another source just to double check pineapple accrual: <a href="https://niftyrank.com/meme-farms/badger-digg">Nifty Rank</a></p>
<p>PiRate = pineapples farmed per day based on staked bdigg.</p>
<p>Please note all column headers are sorted on-click!</p>
<script src="js/sorttable.js">
</script>

<?php
$username = "badgeruser";
$password = "foo";
$hostname = "localhost"; 
$db_name = "badger";

//connection to the database
$dbhandle = mysqli_connect($hostname, $username, $password, $db_name)
 or die("Unable to connect to MySQL");
//echo "Connected to MySQL<br>";

$query = "select nftp.address, nftp.bdigg, nftp.pineapple, nftp.pirate, minted.common, minted.rare, minted.legendary from nftp left outer join minted on nftp.address=minted.address order by nftp.pirate desc";
$result = mysqli_query($dbhandle, $query) or die('Error querying the database.');

//build the table
echo "<table id=\"nfttable\" class=\"sortable\">\n\n";
echo "<tr><th>Address</th><th>bdigg staked</th><th>Pineapples</th>";
echo "<th>PiRate</th><th>HoursToCommon</th><th>HoursToRare</th><th>HoursToLegendary</th>";
echo "<th>Common</th><th>Rare</th><th>Legendary</th></tr>\n";

$index = 1;
//fetch tha data from the database
while ($row = mysqli_fetch_array($result)) {
   $pirate = $row{'pirate'};
   if ( $pirate == 0 ) { $htc = 9999; $htr = 9999;  $htl=9999; } 
   else {
     if ( $row{'pineapple'} > 15 ) { $htc = 0; } else { $htc = (15 - $row{'pineapple'}) / ($pirate / 24); }
     if ( $row{'pineapple'} > 50 ) { $htr = 0; } else { $htr = (50 - $row{'pineapple'}) / ($pirate / 24); }
     if ( $row{'pineapple'} > 100 ) { $htl = 0; } else { $htl = (100 - $row{'pineapple'}) / ($pirate / 24); }
   }
   echo "<tr><td>".$row{'address'}."</td><td>".number_format($row{'bdigg'},4)."</td><td>".number_format($row{'pineapple'},4)."</td>";
   echo "<td>".number_format($row{'pirate'},4)."</td><td>".number_format($htc,2)."</td><td>".number_format($htr,2)."</td><td>".number_format($htl,2)."</td>\n";
   echo "<td>".$row{'common'}."</td><td>".$row{'rare'}."</td><td>".$row{'legendary'}."</td></tr>";   
   $index += 1;
}
echo "</table>";
//close the connection
mysqli_close($dbhandle);
?>
</div>
<script>
var newTableObject = document.getElementById("nfttable");
sorttable.makeSortable(newTableObject);
</body>
</html>
