$(function() {
  $('#tutorial .next').click(function(){
    var nextId = $(this).parents('#tutorial .tab-pane').next().attr("id");
    $('#tutorial [href="#'+nextId+'"]').tab('show');
    return false;
  })

  $('#tutorial a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    //update progress
    var step = $(e.target).data('step');
    var percent = (parseInt(step) / 5) * 100;

    $('#tutorial .progress-bar').css({width: percent + '%'});
    $('#tutorial .progress-bar').text("Step " + step + " of 5");

  })
});
