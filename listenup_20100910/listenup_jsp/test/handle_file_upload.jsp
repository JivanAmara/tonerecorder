<%@ page isThreadSafe="false" %>
<%@ page import="org.apache.commons.fileupload.*, java.util.*, java.io.*" %>

<%! // make a directory if it's not already there
    // if you cannot make it, throw an exception; there's trouble with permissions
    private void makeDirectory(File dir) throws IOException {
        boolean ok = dir.isDirectory();
        if (!ok) {
            ok = dir.mkdir();
        }
        if (!ok && !dir.exists()) {
            throw new IOException("ATTENTION!!! Could not mkdir() " + dir.toString() + ". Change permissions!!!" );
        }
    }
%>

<%
// Servlet to upload a file from an HTML form to test uploading permission and config
// (C) 2003 SoftSynth.com
// Uses Apache Commons FileUpload package.

// TODO - modify these limits if you wish.
    long MAX_FILE_SIZE = 100000; 
    int MAX_MEM_SIZE = 300000;
        
    String TEMP_DIR = null; 

    try {
    	// Get current directory name so we can use
    	// relative names for the temp dir.
        ServletContext servletContext = getServletContext();
        String thisJSPFile = servletContext.getRealPath(request.getServletPath());
        String thisJSPDir = thisJSPFile.substring(0, thisJSPFile.lastIndexOf(File.separator));

        File tempDir = new File (thisJSPDir, "temp");
        makeDirectory(tempDir);
        TEMP_DIR = tempDir.toString();

    }
    catch (IOException e) {
       throw new ServletException("ERROR " + e);
    }

 %>
Upload file using JSP.
<%  
// Set HTTP header via response object so that the result is not cached.
    response.setHeader( "Cache-Control", "private" );
// Use plain text so that ListenUp Applet can easily parse the response.
    response.setContentType( "text/plain" );

// Use buf to store useful messages and echo later to html.
    StringBuffer buf = new StringBuffer();

    boolean isMultipart = FileUpload.isMultipartContent(request);

    DiskFileUpload upload = new DiskFileUpload();
    upload.setSizeThreshold(MAX_MEM_SIZE); // your max memory size
    upload.setSizeMax(MAX_FILE_SIZE);  // your max request size
    upload.setRepositoryPath(TEMP_DIR); // your temp directory

// Parse the multi-part form and extract the fields and file.
    List items = upload.parseRequest(request);
    Iterator iter = items.iterator();
    while (iter.hasNext())
    {
        FileItem item = (FileItem)iter.next();
        // Item is either a form field or a file.  Handle accordingly...
        if (item.isFormField())
        { 
            // Replace this debug printing with handling of various form fields.
            buf.append("name: " + item.getFieldName());
            buf.append(", value: " + item.getString());
            buf.append("\n");
        } else {
            String fieldName = item.getFieldName();
            String contentType = item.getContentType();
            long sizeInBytes = item.getSize();
            String fileName = item.getName();
            
            // Write optional debug info.
            buf.append("FILE:\n  fieldName: " + fieldName + "\n  name: " + fileName +
                     "\n  content type: " + contentType + "\n  size: " + sizeInBytes );          	
            // This next line will appear in Applet status window because SUCCESS is recognized as a marker.
            buf.append("\nSUCCESS - uploaded " + fileName + "\n");
            
			buf.append("By the way, this file was DELETED");

           buf.append("\n\n");
        }
    }
%>

<%= buf.toString() %>

