<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8" />
	<title>Photobooth</title>
	<link rel="stylesheet" href="../common/style.css" />
</head>
<body>
	<main>
		<h1>Photobooth</h1>

		<p>Click on an image to view the animation</p>

<?php
		/* NOTE: If 'image_extension' in the photobooth.py script is changed from jpg, then update the following */
		$thumbs = glob('*.jpg');

		for ($index = 0; $index < count($thumbs); $index++) {
			$image_size = getimagesize($thumbs[$index]);
			$filename_no_ext = substr($thumbs[$index], 0, strrpos($thumbs[$index], "."));

echo <<<END
		<span class="multi-image" style="width: {$image_size[0]}; height: {$image_size[1]}">
			<a href="img-animated.php?img={$filename_no_ext}.gif">
				<img class="lazy" data-original="{$thumbs[$index]}" width={$image_size[0]} height={$image_size[1]}>
			</a>
		</span>

END;
		}
?>

<!--
		<a href="photobooth_photos.zip" class="zipfileImage">
			<img src="photobooth_photo.jpg" height="150">
		</a>
		<h2>Download your photo package</h2>
		<p>Click the following link to download a zip package, containing all your photos, to your computer</p>
		<p><a href="photobooth_photos.zip" class="zipfileLink">Download zip package of all photos</a></p>
-->
		<p>&nbsp;</p>
	</main>

	<!-- Using Lazy Load plugin for JQuery for the images: http://www.appelsiini.net/projects/lazyload -->
	<script src="../common/jquery-2.1.4.min.js"></script>
	<script src="../common/jquery.lazyload.js"></script>
	<script type="text/javascript" charset="utf-8">
	$(function() {
		$("img.lazy").lazyload();
	});
	</script>
</body>
</html>