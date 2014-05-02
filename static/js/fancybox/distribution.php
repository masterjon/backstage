<?php include 'includes/init.php';?>
<!DOCTYPE html>
<html lang="<?php echo $_SESSION["language"]?>">
    <head>
        <?php include 'includes/head.php';?>
        <title>Distribution</title>
    </head>
    
    <body id="distribution">
        <div class="container">
            <?php include 'includes/header.php'?>
            <div id="banner-distribution" class="text-center">
                <img src="images/Distribution/banner_collection.jpg">
            </div>
            <div class="row-fluid" style="padding: 30px">
                <div class="span9">
                    <h1 class="px15 f_body"><?php echo $text["form_title"] ?></h1><br>
                    <form class="row-fluid" id="form-distribution" method="POST" action="">
                        <input type="hidden" value="1" name="sent">
                        <div class="span5">
                            <div><label class="clearfix control-group"><?php echo $text["footer_form_name_label"]?> <input type="text" name="name" data-required="true"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_last_name_label"]?><input type="text" name="lastname" data-required="true"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["footer_form_email_label"]?><input type="text" name="email" data-required="true"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_phone_label"]?><input type="text" name="phone"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_address_label"]?><input type="text" name="address"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_country_label"]?><input type="text" name="country"></label></div>
                        </div>
                        <div class="span5 offset1">
                            <div><label class="clearfix control-group"><?php echo $text["form_city_label"]?><input type="text" name="city"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_state_label"]?><input type="text" name="state"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["form_postal_code_label"]?><input type="text" name="postalcode"></label></div>
                            <div><label class="clearfix control-group"><?php echo $text["footer_form_comment_label"]?><br><textarea  name="comment" style="height:70px;"></textarea></label></div>
                            <div class="text-right"><button class="btn btn-inverse btn-small"><?php echo $text["footer_form_send"]?></button></div>
                        </div>
                        <div class="result"></div>
                            
                    </form>
                </div>
                <div class="span3 text-right">
                    <link rel="stylesheet" href="js/fancybox/jquery.fancybox.css?v=2.1.4" type="text/css" media="screen" />
                    <a class="fancybox" href="images/Distribution/mapa_1.jpg"><img  title="With your help we can go further" src="images/Distribution/mapa.jpg"></a>
                    
                </div>
            </div>
        </div>
        <?php include'includes/footer.php'; ?>
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js "></script>
        <script src="js/jquery.cycle2.js"></script>
        <script src="js/jquery.cycle2.carousel.js"></script>
        <script type="text/javascript" src="js/fancybox/jquery.fancybox.pack.js?v=2.1.4"></script>

        <script>
            $(function(){
                $("#menu-distribution").addClass("active");
                $(".fancybox").fancybox();
            })
        </script>
    </body>
</html>
