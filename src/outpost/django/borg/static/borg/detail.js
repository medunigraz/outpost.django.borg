$(function() {
  var steps = $('#tutorial .tab-pane').length;
  $('#tutorial .progress-bar').attr("aria-valuemax", steps);
  var updateSteps = function(step) {
    var percent = (parseInt(step) / steps) * 100;
    $('#tutorial .progress-bar').css({width: percent + '%'}); $('#tutorial .progress-bar .step').text(step);
    $('#tutorial .progress-bar .steps').text(steps);
    $('#tutorial .progress-bar').attr("aria-valuenow", step);
  };
  $('#tutorial .next').click(function(){
    var nextId = $(this).parents('#tutorial .tab-pane').next().attr("id");
    $('#tutorial [href="#'+nextId+'"]').tab('show');
    return false;
  })

  $('#tutorial a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    //update progress
    var step = $(e.target).data('step');
    updateSteps(step);
  })
  updateSteps(1);
  $('#tutorial').removeClass("hidden");
});
