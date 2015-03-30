$(document).ready(function(){
    $(".execute-btn").on("click", "li",function(){
        var remote_user = $(this).attr('class');
        var command = $("input[name='command']").val();
        var servers = new Array();
        var server_list = $("input[name='server']:checked");
        server_list.each(function(){
            servers.push($(this).val());
        });
        if(command==""){
            return false;
        }
        if(!servers){
            return false;
        }

        $.ajax({
            url: "/execute_cmd",
            type: 'post',
            traditional:true,
            data:{
                'servers': servers,
                'remote_user': remote_user,
                'command': command
            },
            dataType: 'json',
            success: function(response){
                var success = response['success'];
                var fail = response['fail'];
                var success_num = success.length;
                var fail_num = fail.length;
                var total_num = success_num + fail_num;
                var total_msg = success_num + " success, " + fail_num + " fail."
                $("#total").text(total_msg);
                $(".total").text(total_num);
                var html='';
                for(var i= 0; i<success_num; i++){
                    var html = html + '<p class="text-success">' + success[i] + '</p>';
                }
                $("#success").html(html);
                $(".success").text(success_num);
                var html='';
                for(var i= 0; i<fail_num; i++){
                    var html = html + '<p class="text-danger">' + fail[i] + '</p>';
                }
                $("#fail").html(html);
                $(".fail").text(fail_num);
            },
            fail:function(){
                var html = '<p class="text-danger">' +"server occur error" + '</p>';
                $("#total").html(html);
            }
        });
    });

});
