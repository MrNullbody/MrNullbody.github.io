$(document).ready(function () {
  if (document.domain == 'localhost') {
    // Expanded last proofc in localhost (preview)
    $('.proof-collapsible').last().removeClass('proof-collapsible-collapsed').addClass('proof-collapsible-expanded');
  }
  $('.proof-expander.proof-expander-expanding').html('<a><svg height="16" width="16"><path stroke="#999" stroke-width="1.5" fill="none" d="M8 2 L14 8 L8 14"></path></svg></a>');
  $('.proof-expander.proof-expander-collapsing').html('<a><svg height="16" width="16"><path stroke="#999" stroke-width="1.5" fill="none" d="M2 6 L8 12 L14 6"></path></svg></a>');
  $('.proof-expander.proof-expander-ellipsis').html('<span style="font-size:40%">• • •</span>');
  $('.proof-header').append('<div class="floatright"><p><span class="inline-math"><span class="katex"><span class="katex-html" aria-hidden="true"><span class="base"><span class="strut" style="height: 0.675em;"></span><span class="mord amsrm">□</span></span></span></span></span></p></div>');
  $('.proof-expander').click(function () {
    let $this = $(this);
    let $parent = $this.closest('.proof-collapsible');
    if ($parent.length === 0) return;

    let wasCollapsed = !$this.hasClass('proof-expander-collapsing');
    $parent.removeClass('proof-collapsible-collapsed');
    $parent.removeClass('proof-collapsible-expanded');
    $parent.addClass(wasCollapsed ? 'proof-collapsible-expanded' : 'proof-collapsible-collapsed');
  });
});
