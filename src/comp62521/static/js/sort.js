var name;

$(document).ready(function() {
    // find full name, get surname and add it to table as second column

    $('#example td:first-child').each(function() {
        name = preProcess($(this).text());
        $('<td>'+ name +'</td>').insertAfter($(this));
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
    var a = name.split(' ');
    var finalName = [];
    a = a.filter(function(v){
        return ! ( /[0-9]/g ).test(v) ;
    });
    finalName = finalName.concat(a);
    return finalName.slice(-1).pop()
}