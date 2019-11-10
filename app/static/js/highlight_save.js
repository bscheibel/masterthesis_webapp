    function log(){
      console.log("test");

    }

    function set_redis(key, value) {

        $.ajax({
            type: "POST",
            url: "/redis/set/" + key,
            data: JSON.stringify({ value: value }),
            dataType: "json",
            contentType: "json",
            success: function(data)
            {
                (data.GET);
            }
        });
    }

     function get_redis(key) {
        $.ajax({
            type: "GET",
            url: "redis/get/" + key,
            data: "format=json",
            dataType: "text",
            success: function(data)
            {
                $("#result").text(data.GET);
            }
        });
       }

      function split_string(string) {
            var string = str.split(" ",2);
            return string;
        };


    $(document).ready(function(){

        $("input[type=number]").on("change keyup input", function(){
            var array_value = [];
            array_value[0] = $(this).attr('name');
            array_value[1] = $(this).val();

            var key = 'last' + "_" +'{{og_filename}}';

            //console.log({{ dim }});
            set_redis(key, array_value);
        });

        $("input[type=checkbox]").change(function(){

           // Print entered value in a div box
           $("#result").text($(this).attr('name'));
           var key1 = 'last' + "_" +'{{og_filename}}';
           var array_value1 = [];

           if ($(this).is(':checked')) {
                console.log($(this).attr('name') + ' is now checked');
                array_value1[0] = 'relevant.' + $(this).attr('name');
                array_value1[1] = true;
            } else {
                console.log($(this).attr('name') + ' is now unchecked');
                array_value1[0] = $(this).attr('name');
                array_value1[1] = false;
            }

           set_redis(key1, array_value1);

        });



        $("input[type=number]").focus(function(){

            // highlight values, does not work so far

            var number = $(this).attr('name');
            var coords = $(this).attr('data-coords');
            highlight_areas(coords, "red");
            var detail = $(this).attr('data-details');
            console.log(detail, "green");
            highlight_details(detail, "green");

        });

        $("input[type=number]").blur(function(){

          $("div").removeClass("red");
          $("div").removeClass("green");

        });


      function highlight_areas(coords, color){

       let w = {{w}}
       let h = {{h}}
       let pos = $("#drawing").position();
       let drawing_x = pos.left;
       let drawing_y = pos.top;
       let array_coords = coords.split(",");
       let coords_x = parseFloat(array_coords[0]);
       let coords_xmax = parseFloat(array_coords[2]);
       let coords_y = parseFloat(array_coords[1]);
       let coords_ymax = parseFloat(array_coords[3]);
       let coords_width = (coords_xmax - coords_x);

       let coords_height = (coords_ymax - coords_y);


       let width = $("#drawing").width();
       let height = $("#drawing").height();
       let rel_width = coords_width/h*width*1.4;
       let rel_height = coords_height/w*height*1.4;

       let x = width*(coords_x*height/width/w);

       let y = height*(coords_y*width/height/h);
       console.log(w, h, rel_width, rel_height,x,y);

       let $point1 = jQuery("<div class="+color+"/>").css({top: (drawing_y + y -5) + 'px', left: (drawing_x + x-5) + 'px', width: rel_width , height: rel_height});

        $(".images").append($point1);

        };

       function highlight_details(coords, color){

       let w = {{w}}
       let h = {{h}}
       let pos = $("#drawing").position();
       let drawing_x = pos.left;
       let drawing_y = pos.top;
       let array_coords = coords.split(",");
       let coords_x = parseFloat(array_coords[0]);
       let coords_y = parseFloat(array_coords[1]);
       let width_div = (parseFloat(array_coords[2]) - parseFloat(array_coords[0]));

       let height_div = (parseFloat(array_coords[3]) - parseFloat(array_coords[1]));



       let width = $("#drawing").width();
       let rel_width = width_div/h*width;


       let height = $("#drawing").height();
       let rel_height = height*height_div/w;

       let x = width*(coords_x*height/width/w);
       let y= height*(coords_y*width/height/h);
       console.log(rel_width, rel_height);
       if (array_coords[3] > 10000) {
           rel_height = height - y;

       }


       let $point = jQuery("<div class="+color+"/>").css({top: (drawing_y + y) + 'px', left: (drawing_x + x) + 'px', width: (rel_width) + 'px', height: (rel_height) + 'px'});

        $(".images").append($point);

        };

     });
