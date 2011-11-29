/*
 * label2value
 * jquery based script for using form labels as text field values
 * more info on http://cssglobe.com/post/1500/using-labels- 
 *
 * Copyright (c) 2008 Alen Grakalic (cssglobe.com)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 */

this.label2value = function(){	

	// CSS class names
	// put any class name you want
	// define this in external css (example provided)
	var inactive = "inactive";
	var active = "active";
	var focused = "focused";
	
	// function
	$("label").each(function(){		
		obj = document.getElementById($(this).attr("for"));
		if(($(obj).attr("type") == "text") || (obj.tagName.toLowerCase() == "textarea")){			
			$(obj).addClass(inactive);			
			var text = $(this).text();
			$(this).css("display","none");			
			$(obj).val(text);
			$(obj).focus(function(){	
				$(this).addClass(focused);
				$(this).removeClass(inactive);
				$(this).removeClass(active);								  
				if($(this).val() == text) $(this).val("");
			});	
			$(obj).blur(function(){	
				$(this).removeClass(focused);													 
				if($(this).val() == "") {
					$(this).val(text);
					$(this).addClass(inactive);
				} else {
					$(this).addClass(active);		
				};				
			});				
		};	
	});		
};
// on load
$(document).ready(function(){	
	label2value();	
});