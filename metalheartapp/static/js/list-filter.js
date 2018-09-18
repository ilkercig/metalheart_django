
var options = {
    valueNames: [ 'name', 'country' ]
};

var hackerList = new List('artist-list', options);

$( document ).ready(function() {
 
    $( "#genre-selection" ).change(function(){
        console.log( "{{genre.name}}");
    })
 
});