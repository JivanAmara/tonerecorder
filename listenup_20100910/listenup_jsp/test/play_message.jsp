<%
response.setHeader("Cache-Control","no-cache"); //HTTP 1.1
response.setHeader("Pragma","no-cache"); //HTTP 1.0
response.setDateHeader ("Expires", 0); //prevents caching at the proxy server
%>
<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
   <meta name="GENERATOR" content="Mozilla/4.79 [en] (Windows NT 5.0; U) [Netscape]">
   <meta name="KeyWords" content="Java, audio, input, output, JavaSonics, recording, plugin, API">
   <meta name="Description" content="Java API for audio I/O.">
   <title>Play a Voice Message</title>
   
</head>
<body>



<center>
<table callpadding="6" width="90%">
<tr valign="middle">
<td bgcolor="#DCE2E7">
<br>
<center>
<h2>Play a Voice Message using ListenUp
</h2>
</center>
</td>
</tr>
</table>
</center>
<p>
Return to <a href="index.html">home test page<a>.
<p>
This page will play a voice message whose name is passed in the HTTP query.
The filename is specified using the "sampleName" parameter.
See the URL for this page in your browser address bar as an example.
<p>
<%
// The name of the sample to be played is passed using an HTML query parameter.
// The variable is $sampleName.
// The path is relative to UPLOADS_DIR
final String UPLOADS_DIR = "uploads";
String sampleName = request.getParameter("sampleName");
String samplePath = UPLOADS_DIR + "/" + sampleName;
String sampleParam = "<param name=\"sampleURL\"" +
		" value=\"" + samplePath + "\">\n";
%>

<applet
    CODE="com.softsynth.javasonics.recplay.PlayerApplet"
    CODEBASE="../codebase"
    ARCHIVE="JavaSonicsListenUp.jar,OggXiphSpeexJS.jar"
    NAME="ListenUpPlayer"
    WIDTH="220" HEIGHT="70">

	<%= sampleParam %>

</applet>
<p>
If the recorded message is a WAV file recorded using either "adpcm" or "s16" format
then it can also be played directly by the browser.
<p>
<blockquote>
<h3>
<%
	
	// Does the filename end with ".wav"?
	// If so then play it using a link.
	String message;
	if( sampleName.toLowerCase().endsWith( ".wav" ) )
	{
		message = "<a href=\"" + samplePath + "\">Click here to play the message using your browser's WAV player.</a>\n";
	}
	else
	{
		message = "Message is not a WAV file and can only be played using the Applet.\n";
	}
	
%>
	<%= message %>
</h3>
</blockquote>
<p>
(C) 2003 <a href="http://www.softsynth.com" target="_blank">SoftSynth.com</a>,
Phil Burk and Nick Didkovsky
</body>
</html>
