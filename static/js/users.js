function test() {
    console.log("clicked")

    var userID = 34;

    $.ajax({
      type : 'POST',
      url: '/admin/deactivateUser',
      contentType: 'application/json;charset=UTF-8',
      data : {'data':userID},
        error: function () {
            alert("error");
        }
    });
}