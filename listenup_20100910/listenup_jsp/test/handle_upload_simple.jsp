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
// Servlet to upload a file from JavaSonics ListenUp Applet
// Modify this to accept filenames relevant for your purpose.
// This example only permits the upload of files named message_12345.wav or message_12345.spx

// (C) 2003 SoftSynth.com
// Uses Apache Commons FileUpload package.

// TODO - modify these limits if you wish.
    long MAX_FILE_SIZE = 100000; 
    int MAX_MEM_SIZE = 300000;
    
    String UPLOAD_DIR = null; 
    String TEMP_DIR = null; 

    try {
    	// Get current directory name so we can use
    	// relative names for the temp and upload dirs.
        ServletContext servletContext = getServletContext();
        String thisJSPFile = servletContext.getRealPath(request.getServletPath());
        String thisJSPDir = thisJSPFile.substring(0, thisJSPFile.lastIndexOf(File.separator));

        File uploadDir = new File (thisJSPDir, "uploads");
        makeDirectory(uploadDir);
        UPLOAD_DIR = uploadDir.toString();

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

			// NOTE: You should to modify these checks to fit your own needs!!!
		    // Check to make sure the filename is what we expected.
		    // Prevents clowns from overwriting other files.
			// ALso don't let people upload ".php", ".jsp" or other script files to your server.
			// Filename should end with ".wav" or ".spx".
		    // These match the names used by
		    // "listenup_jsp/test/record_upload_wav.html",  "listenup_jsp/test/record_upload_spx.html"		    
		    
			if (fileName.equals("message_12345.wav") || fileName.equals("message_12345.spx")) {
				
            	// Strip path from filename to prevent overwriting system files.
	            int lastSlash = fileName.lastIndexOf( '\\' );
	            if( lastSlash >= 0 ) fileName = fileName.substring( lastSlash + 1 );
    	        lastSlash = fileName.lastIndexOf( '/' );
        	    if( lastSlash >= 0 ) fileName = fileName.substring( lastSlash + 1 );
                       
            	String pathName = UPLOAD_DIR + "/" + fileName;
            
    	        File uploadedFile = new File( pathName );
	            item.write(uploadedFile);

        	    // Write optional debug info.
            	buf.append("FILE:\n  field: " + fieldName + "\n  file name: " + fileName +
                     "\n  content type: " + contentType + "\n  size: " + sizeInBytes );
	            // buf.append("\nYour file was uploaded and renamed to \n      " + pathName + "\n");

        	    // IMPORTANT!
            	// This next line will appear in Applet status window because SUCCESS is recognized as a marker.
            	// You must output SUCCESS for Applet to know upload went ok
            	buf.append("\nSUCCESS - uploaded " + fileName + "\n");
			} else {
				buf.append("ERROR: This JSP example only permits the uploading of files named message_12345.spx or message_12345.wav, not " + fileName);
			}			
           buf.append("\n\n");
        }
    }
%>

<%= buf.toString() %>

