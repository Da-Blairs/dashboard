/**
 * Simple JS Clock and Date Updater
 */
(function() {

  var Clock = function () {
    
    var timeElement = document.querySelector('#time');
    var dateElement = document.querySelector('#date');
    
    /**
     * Time and Date Format
     */
    var timeFormat = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute:'2-digit'
    });
    
    var dateFormat = new Date().toLocaleDateString([], {
      month: 'short', 
      day: 'numeric'
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
     * Pass vars to our Render Util
     */
    render(timeFormat, timeElement);
    render(dateFormat, dateElement);
  }
  
  /**
   * Start the Clock Interval
   */
  window.setInterval(Clock, 1000);

}());
