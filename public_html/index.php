<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <meta name="description" content="">
  <meta name="author" content="">

  <title>digg.finance</title>

  <!-- Bootstrap core CSS -->
  <link href="vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">

  <!-- Custom styles for this template -->
  <link href="css/scrolling-nav.css" rel="stylesheet">
  <link href="css/styled-table.css" rel="stylesheet">
  <link href="css/mygrid.css" rel="stylesheet">

</head>

<body id="page-top">

  <!-- Navigation -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" id="mainNav">
    <div class="container">
      <a class="navbar-brand js-scroll-trigger" href="#page-top">DIGG</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarResponsive">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link js-scroll-trigger" href="#info">Info</a>
          </li>
          <li class="nav-item">
            <a class="nav-link js-scroll-trigger" href="#history">History</a>
          </li>
          <li class="nav-item">
            <a class="nav-link js-scroll-trigger" href="#badger">Badger</a>
          </li>
          <li class="nav-item">
            <a class="nav-link js-scroll-trigger" href="nft.php">NFT</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <header class="bg-primary text-white">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 mx-auto">

          <h1>Welcome to digg.finance</h1>
          <p class="lead">An **unofficial** website for BadgerDAO and the DIGG token</p>
        </div>
      </div>
    </div>
  </header>

  <?php
  $username = "diggreader";
  $password = "foo";
  $hostname = "localhost";
  $db_name = "digg";

  //connection to the database
  $dbhandle = mysqli_connect($hostname, $username, $password, $db_name)
   or die("Unable to connect to MySQL");
  //echo "Connected to MySQL<br>";

  $query = "SELECT * FROM running_prices ORDER BY timestamp DESC LIMIT 1";
  $result = mysqli_query($dbhandle, $query) or die('Error querying the database.');

  //establish variables
  while ($row = mysqli_fetch_array($result)) {
    $pricets = $row{'timestamp'};
    $btcusd = $row{'BTCUSDprice'};
    $diggbtc = $row{'DIGGBTCprice'};
    $diggusd = $row{'DIGGUSDprice'};
  }

  $query = "SELECT * FROM calc_rebase ORDER BY timestamp DESC LIMIT 1";
  $result = mysqli_query($dbhandle, $query) or die('Error querying the database.');

  //establish variables
  while ($row = mysqli_fetch_array($result)) {
    $latestrb = $row{'timestamp'};
    $latestsupply = $row{'supply'};
    $latestdelta = $row{'delta'};
    $latestrbpct = $row{'rbpct'};
  }

  mysqli_close($dbhandle);
  ?>

  <section id="info">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 mx-auto">
          <h2>DIGG information</h2>
          <p class="lead">Current as of <?php echo $pricets ?> UTC from Chainlink Oracles</p>
          <div class="gridcontainer3">
            <div class="item">DIGG/BTC Price:<br><?php echo $diggbtc; ?>₿</div>
            <div class="item">DIGG/USD Price:<br>$<?php echo number_format($diggusd,2); ?></div>
            <div class="item">BTC/USD Price:<br>$<?php echo number_format($btcusd,1); ?></div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-lg-8 mx-auto">
          <P></p>
          <p class="lead">Ping <a href="https://telegram.me/diggrebasebot">@diggrebasebot</a> for a summary of this information on Telegram.</p>
          </div>
        </div>
      </div>

    </div>
  </section>

  <section id="history" class="bg-light">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 mx-auto">
          <h2>Rebase History</h2>
            <?php 
            $dbhandle = mysqli_connect($hostname, $username, $password, $db_name)
              or die("Unable to connect to MySQL");
            //echo "Connected to MySQL<br>";

            $query = "SELECT * FROM calc_rebase ORDER BY timestamp DESC";
            $result = mysqli_query($dbhandle, $query) or die('Error querying the database.');

            //build the table
            echo "<table class=\"styled-table\">\n\n";
            echo "<tr><td>Tx ID</td><td>UTC Rebase Time</td><td>Supply</td><td>Delta</td></tr>";

            //fetch tha data from the database
            while ($row = mysqli_fetch_array($result)) {
            echo "<tr><td><a href=\"https://etherscan.io/tx/".$row{'txid'}."\">Etherscan</a></td><td>".$row{'timestamp'}."</td><td>".$row{'supply'}."</td><td>".$row{'rbpct'}."%</td></tr>\n";

            }
            echo "</table>";
            //close the connection
            mysqli_close($dbhandle);
            ?>

        </div>
      </div>
    </div>
  </section>

  <section id="badger">
    <div class="container">
      <div class="row">
        <div class="col-lg-8 mx-auto">
          <h2>Badger DAO</h2>
          <p class="lead"></p>
          <p class="lead">Please visit <a href="https://badger.finance/digg">the official badger website</a> for more information!</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="py-5 bg-dark">
    <div class="container">
      <p class="m-0 text-center text-white">Copyright &copy; digg.finance 2021</p>
    </div>
    <!-- /.container -->
  </footer>

  <!-- Bootstrap core JavaScript -->
  <script src="vendor/jquery/jquery.min.js"></script>
  <script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>

  <!-- Plugin JavaScript -->
  <script src="vendor/jquery-easing/jquery.easing.min.js"></script>

  <!-- Custom JavaScript for this theme -->
  <script src="js/scrolling-nav.js"></script>

</body>

</html>
