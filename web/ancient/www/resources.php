<?php

$flag = trim(file_get_contents("/run/secrets/flag.txt"));

$flag_length = strlen($flag);

$salt = md5(md5($flag));

$answers = "2010BrianThe Lesser of Two Evils".$flag;

?>
