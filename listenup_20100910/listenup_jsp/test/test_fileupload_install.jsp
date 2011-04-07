<html>
<head>
<title>Test org.apache.commons.fileupload installation</title>
</head>

<body>

<%@ page isThreadSafe="false" %>
<%@ page import="org.apache.commons.fileupload.*" %>

<% // Check that we have a file upload request
	boolean isMultipart = FileUpload.isMultipartContent(request);
%>

<FONT SIZE=4>Test Commons FileUpload installation <br>
If you can read this instead of getting a ServletException, then org.apache.commons.fileupload.FileUpload is 
found in this webapp's classpath, and was installed ok!<br><br>
</FONT>
Diagnostic info: 
<% if (isMultipart) { %>
The request sent to this jsp page is a multipart request
<% } else { %>
The request sent to this jsp page is not a multipart request
<% } %>
<BR><BR>
<A HREF="index.html">Back</A>
</body>
</html>