<%@ Page Language="C#" %>

<script runat="server">

    private void Page_Load(object sender, EventArgs e)
    {
 
	/* This must come before anything else is printed so it gets in the header. */
	    Response.ContentType = "text/plain";

	/* Clear out any existing response headers */
	    Response.Clear();
	    
	/* Buffer response, so no output sent until we're through */
	    Response.BufferOutput = true;

	/* Grab the first file from the Request */
	    HttpPostedFile f = Request.Files[0];

	/* Get user comment posted variable */
	    String userComment = Request.Form["userComment"];	    

	/* Print relevent file information provided by HttpPostedFile object for debugging. */
	    Response.Write( String.Format("{0,-12}= {1}\n", "name", f.FileName) );
	    Response.Write( String.Format("{0,-12}= {1}\n", "type", f.ContentType) );
	    Response.Write( String.Format("{0,-12}= {1}\n", "size", f.ContentLength) );
	    Response.Write( String.Format("{0,-12}= {1}\n", "userComment", userComment) );

	    Response.Write ("\nSUCCESS file was uploaded");
	    Response.Write ("\nBy the way, your uploaded file was not saved to the server.");
	    Response.Write ("\nHit BACK button in browser to continue testing.");
	    
	/* Send output */
	    Response.Flush();
	
    }

</script>

