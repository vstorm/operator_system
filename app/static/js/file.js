$(document).ready(function () {
    $('.file-select').bootstrapDualListbox({
        bootstrap2Compatible: false,
        moveAllLabel: 'MOVE ALL',
        removeAllLabel: 'REMOVE ALL',
        moveSelectedLabel: 'MOVE SELECTED',
        removeSelectedLabel: 'REMOVE SELECTED',
        filterPlaceHolder: 'FILTER',
        filterSelected: '2',
        filterNonSelected: '1',
        moveOnSelect: true,
        preserveSelectionOnMove: 'all',
        helperSelectNamePostfix: '_myhelper',
        selectedListLabel: 'Selected Files',
        nonSelectedListLabel: 'UnSelected Files'
    })
//                .bootstrapDualListbox('setMoveAllLabel', 'Move all teh elementz!!!')
//                .bootstrapDualListbox('setRemoveAllLabel', 'Remove them all!')
        .bootstrapDualListbox('setSelectedFilter', undefined)
        .bootstrapDualListbox('setNonSelectedFilter', undefined)
        .bootstrapDualListbox('refresh');
    $(".execute-btn").on("click", "li", function () {
        var files;
        var remote_user = $(this).attr('class');
        var servers = new Array();
        var trans_type = $("[name='trans-type']").val();
        var server_list = $("input[name='server']:checked");
        var remote_path = $("[name='remote_path']").val();
        server_list.each(function () {
            servers.push($(this).val());
        });
        if (trans_type == "getfile") {
            files = $("input[name='file']").val();
        }
        else {
            files = new Array();
            $("#bootstrap-duallistbox-selected-list_myselect option").each(function () {
                files.push($(this).val());
            });
        }

        $.ajax({
            url: "/transfer_file",
            type: 'post',
            traditional: true,
            data: {
                'servers': servers,
                'remote_user': remote_user,
                'trans_type': trans_type,
                'files': files,
                'remote_path': remote_path
            },
            dataType: 'json',
            success: function (response) {
                var success = response['success'];
                var fail = response['fail'];
                var success_num = success.length;
                var fail_num = fail.length;
                var total_num = success_num + fail_num;
                var total_msg = success_num + " success, " + fail_num + " fail."
                $("#total").text(total_msg);
                $(".total").text(total_num);
                var html = '';
                for (var i = 0; i < success_num; i++) {
                    var html = html + '<p class="text-success">' + success[i] + '</p>';
                }
                $("#success").html(html);
                $(".success").text(success_num);
                var html = '';
                for (var i = 0; i < fail_num; i++) {
                    var html = html + '<p class="text-danger">' + fail[i] + '</p>';
                }
                $("#fail").html(html);
                $(".fail").text(fail_num);
            },
            fail: function () {
                var html = '<p class="text-danger">' + "server occur error" + '</p>';
                $("#total").html(html);
            }
        });
    });
});