<?php
	if (isset($_GET["photo_code"]))
		header('Location: '.$_GET["photo_code"]);
?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title>Photobooth</title>
	<link rel="stylesheet" href="common/style.css" />
</head>
<body>
	<main>
		<h1>Photobooth</h1>

		<p><strong>Please enter your photobooth code in the box below, and click 'submit'</strong></p>
		<form action="index.php" method="GET">
			<p>Photobooth code: <input type="text" name="photo_code" value=""></p>
			<p><input type="submit" value="Submit"></p>
		</form>
	</main>
</body>
</html>