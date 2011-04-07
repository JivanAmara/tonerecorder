// Decide whether to EMBED JavaSonics Plugin for Navigator.
// Author: Phil Burk 2001
	
// Is it a type of Netscape browser?
var app = navigator.appName.toLowerCase();
var is_netscape = (app.indexOf("netscape") != -1 );

// Is it iCab for Macintosh masquerading as a Netscape browser?
var agt = navigator.userAgent.toLowerCase();
var is_icab = (agt.indexOf("icab") != -1);

// Is it a Macintosh?
var platform = navigator.platform.toLowerCase();
var is_mac = (agt.indexOf("mac") != -1);

var appversion = parseFloat(navigator.appVersion); 

if( !navigator.javaEnabled() )
{
	document.writeln("<P><B>Java is NOT enabled for your browser.");
	document.writeln("Cannot run JavaSonics without Java!</B><P>");
}
// Mac Netscape 6 uses MRJ and PC Netscape uses real Java!
else if( is_netscape && !is_icab && (appversion < 5.0) )
{
// If we are running an old Netscape browser then we should use the Netscape Plugin.
// Has the plugin been installed?
// Check for name that we used on both Mac and PC.
	var jsonicsPcPlugin = navigator.plugins["SoftSynth JavaSonics"];
	var jsonicsMacPlugin = navigator.plugins["npJSonics"];
	if( (jsonicsMacPlugin == undefined) && (jsonicsPcPlugin == undefined))
	{
		document.writeln("<p><b>ERROR:</b> The JavaSonics plugin could not be found!");
		document.writeln("You can download the free JavaSonics plugin from ");
		document.writeln('<A HREF="http://www.javasonics.com/plugins">here</A>.<P>');
	}
	else
	{
	// check property on global navigator object to see if plugin window already open
	// If open, don't open it again because Netscape may hang if
	// the garbage collector is running, or if threads call the plugin
	// while we are EMBEDding plugin.
		jsonicsPluginWindow = navigator.jsonicsPluginWindow;
		if (jsonicsPluginWindow)
		{
			document.writeln("Using already open JavaSonics Plugin Window.<P>");
		}
		else
		{
	// not open so we had better open it now
			navigator.jsonicsPluginWindow = window.open("embed_javasonics_plugin.html",
				"SharedJavaSonicsWindow",
				"toolbar=no,resizable=yes,scrollbars=yes,height=240,width=520");
			document.writeln("Opened Plugin Window for JavaSonics.<P>");
		}
	}
}
else
{
// For Internet Explorer or iCab or NS6, don't try to EMBED the Netscape Plugin because IE may crash.
	document.writeln("<P>This Applet requires the JavaSonics plugin.");
	document.writeln("If the Applet fails to run, you can download the free JavaSonics plugin from ");
	document.writeln('<A HREF="http://www.javasonics.com/plugins">here</A>. ');
	document.writeln("After downloading the plugin, if you still see an error, then hold down the ");
	document.writeln( is_mac ? "shift-key " : "control-key " );
	document.writeln("and click on the Refresh button in the toolbar above.<P>");
}
