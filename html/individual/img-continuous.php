<?php
	$img_filename = "";
	if (isset($_GET["img"]))
		$img_filename = $_GET["img"];
?>

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title>Photobooth Image</title>
	<link rel="stylesheet" href="../common/style.css" />
</head>
<body>
	<main>
		<h1>Photobooth Image</h1>

<?php
	if (empty($img_filename) || (file_exists($img_filename) === FALSE)) {
echo <<<END
		<p>Parameter 'img' missing from URL, or image not found.</p>
END;
	} else {
echo <<<END
		<img src="{$img_filename}">

		<p>To download the image, right-click it and select 'Save Image As...' (or the equivalent in your web browser)</p>
END;
}
?>

	</main>
</body>
</html>