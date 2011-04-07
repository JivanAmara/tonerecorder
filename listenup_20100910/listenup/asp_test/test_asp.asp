<% @Language=VBScript %>
<% Option Explicit %>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html><!-- InstanceBegin template="/Templates/sdkDoc.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="../style_sdk.css" rel="stylesheet" type="text/css"/>
<!-- InstanceBeginEditable name="doctitle" -->
<title>Test ASP Installation</title>
<!-- InstanceEndEditable --><!-- InstanceBeginEditable name="head" -->

   <meta name="GENERATOR" content="Mozilla/4.79 [en] (Windows NT 5.0; U) [Netscape]">
   <meta name="KeyWords" content="Java, audio, input, output, JavaSonics, recording, plugin, API">
   <meta name="Description" content="Java API for audio I/O.">


<!-- InstanceEndEditable -->
</head>
<body>
<center>
  <table width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr valign="middle">
      <td width="200" bgcolor="#DCE2E7"><center>
          <font color="#FF9933" size="+2"><strong><em><a href="http://www.javasonics.com/" target="_top"> <font face="Verdana, Arial, Helvetica, sans-serif">JavaSonics</font></a></em> </strong></font>
        </center></td>
      <td width="60" bgcolor="#DCE2E7"><center>
          <h1>SDK</h1>
        </center></td>
      <td bgcolor="#DCE2E7"><center>
          <h1><!-- InstanceBeginEditable name="mainHeading" -->Test ASP On Server <!-- InstanceEndEditable --></h1>
        </center></td>
    </tr>
  </table>
</center>
<table width="100%" border="0" cellpadding="0" cellspacing="0" >
  <tr>
    <td valign="top" width="100" bgcolor="#D7E5F2"><br>
      <p><a class="sidenavbar" href="http://www.javasonics.com/" target="_top">Web&nbsp;Home</a></p>
      <p><a class="sidenavbar" href="../index.html" target="_top">SDK&nbsp;Home</a></p>
      <p><a class="sidenavbar" href="../docs/index.html" target="_top">Docs</a></p>
      <p><a class="sidenavbar" href="../php_test/index.html" target="_top">Test&nbsp;PHP</a></p>
      <p><a class="sidenavbar" href="index.html" target="_top">Test&nbsp;ASP</a></p>
      <p><a class="sidenavbar" href="../asp_net_test/index.html" target="_top">Test&nbsp;ASP.NET</a></p>
      <p><a class="sidenavbar" href="../examples/index.html" target="_top">Examples</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/demos/" target="_top">Demos</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/downloads/" target="_top">Download</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/sales/" target="_top">Purchase</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/support/" target="_top">Support</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/forum/" target="_top">Forum</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/login/" target="_top">Login</a></p>
      <p><a class="sidenavbar" href="http://www.javasonics.com/contacts.php" target="_top">Contact&nbsp;Us</a></p>
      <p><a class="sidenavbar" href="http://www.mobileer.com/" target="_blank">Company</a></p>
      <br>
    </td>
    <td valign="top"><div class="primary"> <!-- InstanceBeginEditable name="primaryContent" -->

<center>
</center>
<p>
You should see a message that says "ASP is Working!" below.
<p>
<blockquote>
<pre>
<%
	' IF YOU SEE THIS ASP COMMENT IN YOUR BROWSER THEN ASP IS NOT WORKING!
	' PERHAPS THIS IS A LINUX SERVER AND NOT AN IIS SERVER!
	Response.Write "ASP is " ' NOT
	Response.Write "Working!<BR>"
	Response.Write "Current ASP Version = " & Request.ServerVariables("SERVER_SOFTWARE") & "<BR>"
%>
</pre>
</blockquote>
<p>If not, make sure you've set the listenup/asp_test folder to be an application,
  and to allow scripts to execute.</p>
<p>
Also make sure that the Web Host is your website and not ours.
<p>
<blockquote>
<pre>
<%
	Response.Write "Web Host = " & Request.ServerVariables("SERVER_NAME") & "<BR>"
%>
</pre>
</blockquote>
<p>[<a href="index.html">Test Home</a>] [<a href="play_welcome.html">Previous</a>] [<a href="test_post.asp">Next</a>]
<!-- InstanceEndEditable --> </div></td>
  </tr>
</table>
<br>
<div align="left"> &copy; 2001-2006 <a href="http://www.mobileer.com/">Mobileer, Inc.</a> &nbsp;&nbsp;This page is from the ListenUp&nbsp;SDK. You can download the SDK from <a href="http://www.javasonics.com/downloads/">here</a>.</div>
</body>
<!-- InstanceEnd --></html>
