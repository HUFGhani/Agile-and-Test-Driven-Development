var name;
$(document).ready(function() {
    // find full name, get surname and add it to table as second column
    $('#example td:first-child').each(function() {
        name = preProcess($(this).text());
      $('<td>'+ name.split(' ')[1]+'</td>').insertAfter($(this));
    });
    // configure sorting
    $('#example').DataTable( {
        'columnDefs': [
          {'orderData':[1], 'targets': [0]},
          {
            'targets': [1],
            'visible': false,
            'searchable': false
          },
        ],
    } );
});


function preProcess(name) {
    var a = name;
    if(name.split(" ").length == 2) {
        a = a.replace(/[\{\(\)\}]+/g, '');
        a = a.replace(/[0-9]+/g, '');
    }else if(name.split(" ").length == 3){
   a = a.replace(/[\{\(\)\}]+/g, '');
        a = a.replace(/[0-9]+/g, '');
    }else if(name.split(" ").length == 4) {
   a = a.replace(/[\{\(\)\}]+/g, '');
        a = a.replace(/[0-9]+/g, '');
    }
    return a
}