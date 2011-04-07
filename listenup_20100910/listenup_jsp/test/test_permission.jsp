<HTML>

<HEAD>
    <TITLE>Permission Test</TITLE>
</HEAD>
<BODY>

<%@ page import="java.util.*, java.io.*, java.net.*" %>

<%  StringBuffer buf = new StringBuffer();
    boolean ok = false;
try {
        ServletContext servletContext = getServletContext();
        String thisJSPFile = servletContext.getRealPath(request.getServletPath());
        String thisJSPDir = thisJSPFile.substring(0, thisJSPFile.lastIndexOf(File.separator));
        buf.append(thisJSPFile + "<br>");
        buf.append(thisJSPDir + "<br>");
        File newDir = new File (thisJSPDir, "junk");
        ok = newDir.mkdir();
        if (!ok && !newDir.exists()) {
            throw new IOException("ATTENTION!!! Could not mkdir() " + newDir.toString() + ". Change permissions!!!" );
        }
        File textFile = new File(newDir, "test.txt");
        PrintWriter pout = new PrintWriter(new FileOutputStream(textFile));
        pout.println("This is a line of text written by test_permission.jsp to test writing a new file");
        pout.close();

        if (!textFile.exists() || textFile.length() == 0) {
            throw new ServletException("Tried writing " + textFile.toString() + ", but the file was not created or is empty.");
        }
        ok = textFile.delete();
        if (!ok) { 
            throw new ServletException("Tried deleting test file " + textFile.toString() + ", but could not");
        }
        ok = newDir.delete();
        if (!ok) { 
            throw new ServletException("Tried deleting test dir " + newDir.toString() + ", but could not.");
        }
   }
   catch (SecurityException e) {
       throw new ServletException("Permissions error, ask webmaster for assistance. " + e);
   }
%>

Congratulations.  If you can read this, your JSP page has the proper permissions to handle file uploads.<BR>

</FONT>
<BR><BR>
<A HREF="index.html">Back</A>
</BODY>
</HTML>

