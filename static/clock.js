/**
 * Simple JS Clock
 */
(function() {

  var Clock = function () {
    
    var el = document.querySelector('#js-clock');
    
    /**
     * Time Format
     */
    var timeFormat = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute:'2-digit',
      second:'2-digit'
    });
     
    /** 
     * Render Util
     */
    render = function(template, node) {
      
      if (!node) return;
      node.innerHTML = (typeof template === 'function' ? template() : template);
      
      var event = new CustomEvent('elementRenderer', {
        bubbles: true
      });
      
      node.dispatchEvent(event);
      return node;
    };
    
    /**
     * Pass vars to out Render Util
     */
    render(timeFormat, el);
  }
  
  /**
   * Start the Clock Interval
   */
  window.setInterval(Clock, 1000);

}());
