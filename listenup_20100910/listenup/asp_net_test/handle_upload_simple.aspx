<%@ Page Language="C#" Debug="true" %>
<%@ Import namespace="System.IO" %>

<script runat="server">
/*
 * HTML File Upload processor
 * (C) 2009 Mobileer Inc, www.javasonics.com
 * adapted by Robert Marsanyi
 * This version handles file upload in a simple way.

 * IMPORTANT - MAKE THESE CHANGES to fit your application.
 *  1) Change check for the file name to match your naming system.
 *  2) Change or remove the upfile_size_limit code.
 *  3) Change the uploads_dir to match your desired directory.
 *  4) Get your own variables from the POST like userName or whatever.
 */

private void Page_Load(object sender, EventArgs e)
{

// Define directory to put file in.
// It must have read/write permissions accessable your web server.

	String uploads_dir = "../uploads";

// Set maximum file size that your script will allow.
// Note that .Net imposes it's own maximum size for Requests, which can be
// overridden in Machine.config or Web.config.  See .Net docs for details.

    	long upfile_size_limit = 500000;
	long upfile_size;
	
	HttpPostedFile file;
	FileInfo fileInfo;
	double duration;
	String raw_name;
	String upfile_name;
	bool err = false;
	
// These must come before anything else is printed so that they get in the header.
    	Response.ContentType = "text/plain";
	Response.Clear();

// Applet always sends duration in seconds along with file.
	try
	{
        	duration = Convert.ToDouble( Request.Form["duration"] );
		Response.Write( String.Format("{0,-13} = {1}\n", "duration", duration) );
        }
        catch( Exception )
        {
		Response.Write( "ERROR - duration parameter is invalid.\n" );
		duration = 0;
		err = true;
	}

// Extract information provided by HttpPostedFile object
        file = Request.Files["userfile"];
        if ( file != null )
        {
		upfile_size = file.ContentLength;
		raw_name = file.FileName;
		fileInfo = new FileInfo( raw_name );
		upfile_name = fileInfo.Name;

// NOTE: you can change upfile_name to anything you want. You can build names
// based on a database ID or hash index, etc.

// Print relevent file information for debugging.
		Response.Write( String.Format("{0,-13} = {1}\n", "raw_name", raw_name) );
		Response.Write( String.Format("{0,-13} = {1}\n", "name", upfile_name) );
		Response.Write( String.Format("{0,-13} = {1}\n", "type", file.ContentType) );
		Response.Write( String.Format("{0,-13} = {1}\n", "size", upfile_size) );
		Response.Write( String.Format("{0,-13} = {1}\n", "Upload dir", uploads_dir) );
		Response.Write( String.Format("{0,-13} = {1}\n", "path", file.FileName) );

/*
 * WARNING - IMPORTANT SECURITY RELATED INFORMATION!
 * You should to modify these checks to fit your own needs!!!
 * Check to make sure the filename is what you expected to
 * prevent hackers from overwriting other files.
 * Also don't let people upload ".asp" or other script files to your server.
 * Filename should end with ".wav" or ".spx".
 * For applications, we recommend building a filename from scratch based on
 * user information, time, etc.
 * These match the names used by
 * "test/record_upload_wav.html",  "test/record_upload_spx.html"
 * and "speex/record_speex.html".
 */

		if( (String.Compare(upfile_name,"message_12345.wav") != 0)
			&& (String.Compare(upfile_name,"message_12345.spx") != 0)
			&& (String.Compare(upfile_name,"message_xyz.wav") != 0)
			&& (String.Compare(upfile_name,"message_xyz.spx") != 0)
		)
		    {
			Response.Write( String.Format("ERROR - filename {0} rejected by your script.\n", upfile_name) );
			err = true;
		    }

		if( upfile_size > upfile_size_limit)
		{
			Response.Write( String.Format("ERROR - script says file too large, {0} > {1}\n", upfile_size, upfile_size_limit) );
			err = true;
		}
	
		if( !err )
		{

// Resave file in public local directory.
			try
			{
				file.SaveAs( Server.MapPath(uploads_dir + "/" + upfile_name) );
			}
			catch( Exception )
			{
				Response.Write( "ERROR - file.SaveAs failed! See Java Console.\n" );
				err = true;
			}
		}

		if( !err )  
		{
			Response.Write( String.Format("SUCCESS - {0} uploaded.\n", upfile_name) );
		}
	}
	else
	{
		Response.Write( "ERROR - you haven't uploaded a file.\n" );
		err = true;
	}
	
}

</script>