<?php 
  function mail_utf8($to, $subject = '(No subject)', $message = '', $header = '') 
                {
     $header_ = 'MIME-Version: 1.0' . "\r\n" . 'Content-type: text/plain; charset=UTF-8' . "\r\n";
     return mail($to, '=?UTF-8?B?'.base64_encode($subject).'?=', $message, $header_ . $header);
                    
                }

if(!empty($_POST)){
	$nombre=$_POST['nombre'];
	$correo=$_POST['email'];
	$fecha=$_POST['fecha'];
	$nacionalidad=$_POST['nacionalidad'];
}
$to="german@punkmkt.com";

$subject = 'Nuevo mensaje: Landing backstage';  
            $headers= "From: ".$nombre."<".$correo.">" . "\r\n";
            //$headers .= 'Bcc: sebas@punkmkt.com,german@punkmkt.com' . "\r\n";

		$mensaje='Nuevo comentario por parte de: '.$nombre.' <'.$correo."> .";
        $mensaje.="Fecha de nacimiento:".$fecha."\n";
        $mensaje.="Nacionalidad:".$nacionalidad."\n";
mail( $to, $subject, $mensaje, $headers );
