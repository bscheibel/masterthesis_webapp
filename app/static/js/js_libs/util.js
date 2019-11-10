$B64 = function(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
    function toSolidBytes(match, p1) {
      return String.fromCharCode('0x' + p1);
  }));
}

$.fn.to_em_raw = function(settings){
  settings = jQuery.extend({
      scope: 'body'
  }, settings);
  var that = parseInt(this[0]||"0",10),
      scopeTest = jQuery('<div style="display: none; font-size: 1em; margin: 0; padding:0; height: auto; line-height: 1; border:0;">&nbsp;</div>').appendTo(settings.scope),
      scopeVal = scopeTest.height();
  scopeTest.remove();
  return (that / scopeVal).toFixed(8);
};
$.fn.to_em = function(settings){
  return $(this[0]).to_em_raw(settings) + 'em';
};

$.fn.get_val = function () {
  if ($(this).is('input') || $(this).is('select') || $(this).is('textarea')) {
    return $(this).val();
  } else {
    var ret = $(this).html().replace(/<div>/g,'').replace(/<\/div>/g,'\n').replace(/<br\/?>/g,'\n').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,'\'').trim();
    if (ret == '') $(this).empty();
    return ret;
  }
};
$.fn.set_val = function (val) {
  if ($(this).is('input') || $(this).is('select') || $(this).is('textarea')) {
    $(this).val(val);
  } else {
    $(this).text(val);
  }
};
$.fn.serializePrettyXML = function () {
  return vkbeautify.xml(this.serializeXML(),'  ');
};

$.fn.serializeXML = function () {
  var out = '';
  if (typeof XMLSerializer == 'function') {
      var xs = new XMLSerializer();
      this.each(function() {
          out += xs.serializeToString(this);
      });
  } else if (this[0] && this[0].xml != 'undefined') {
      this.each(function() {
          out += this.xml;
      });
  }
  return out;
};
$.fn.serializePrettyXML = function () {
  return vkbeautify.xml(this.serializeXML(),'  ');
};

String.prototype.repeat = function(num) {
  return new Array(num + 1).join(this);
};

String.prototype.unserialize = function() {
  var data = this.split("&");
  var ret = new Array();
  $.each(data, function(){
      var properties = this.split("=");
      ret.push([properties[0], properties[1]]);
  });
  return ret;
};

$XR = function(xmlstr) {
  if (typeof xmlstr == "string") {
    return $.parseXML(xmlstr);
  } else {
    return $(xmlstr.ownerDocument || xmlstr);
  }
};

$X = function(xmlstr) {
  return $($.parseXML(xmlstr).documentElement);
};
