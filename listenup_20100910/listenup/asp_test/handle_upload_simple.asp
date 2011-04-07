<!--#include file="common_functions.asp"-->
<%
' HTML File Upload processor
' (C) 2009 Mobileer Inc, www.javasonics.com
' adapted by Robert Marsanyi
' This version handles file upload in a simple way.
'
' IMPORTANT - MAKE THESE CHANGES to fit your application.
'  1) Change check for the file name to match your naming system.
'  2) Change or remove the upfile_size_limit code.
'  3) Change the uploads_dir to match your desired directory.
'  4) Get your own variables from the POST like userName or whatever.

' Define directory to put file in.
' It must have read/write permissions accessable your web server.
	uploads_dir = "../uploads"

' Set maximum file size that your script will allow.
    upfile_size_limit = 500000

' These must come before anything else is printed so that they get in the header.
    Response.ContentType = "text/plain"

' Instantiate an ASPUpload object
	Set upload = Server.CreateObject("Persits.Upload")
	upload.Save  ' in memory

' Get posted variables.
    duration = strip_tags(upload.Form("duration"))

' Extract information provided by ASPUpload object.
	Set file = upload.Files("userfile")
    upfile_size = file.Size
	raw_name = file.OriginalPath
    upfile_name = file.OriginalFileName

    ' NOTE: you can change upfile_name to anything you want. You can build names
    ' based on a database ID or hash index, etc.

	' Print relevent file information provided by ASPUpload objects for debugging.
    Response.Write "raw_name     = " & raw_name & vbLF
    Response.Write "name         = " & upfile_name & vbLF
    Response.Write "type         = " & file.ContentType & vbLF
    Response.Write "size         = " & upfile_size & vbLF
    Response.Write "Upload dir   = " & uploads_dir & vbLF
	Response.Write "path         = " & file.Path & vbLF

' Applet always sends duration in seconds along with file.
    Response.Write "duration     = " & duration & vbLF

	' WARNING - IMPORTANT SECURITY RELATED INFORMATION!
    ' You should to modify these checks to fit your own needs!!!
    ' Check to make sure the filename is what you expected to
    ' prevent hackers from overwriting other files.
	' Also don't let people upload ".asp" or other script files to your server.
	' Filename should end with ".wav" or ".spx".
	' For applications, we recommend building a filename from scratch based on
	' user information, time, etc.
    ' These match the names used by
    ' "test/record_upload_wav.html",  "test/record_upload_spx.html"
    ' and "speex/record_speex.html".
    if( (StrComp(upfile_name,"message_12345.wav") <> 0) and _
        (StrComp(upfile_name,"message_12345.spx") <> 0) and _
        (StrComp(upfile_name,"message_xyz.wav") <> 0) and _
        (StrComp(upfile_name,"message_xyz.spx") <> 0) _
      ) then
        Response.Write "ERROR - filename " & upfile_name & " rejected by your ASP script." & vbLF
    elseif( upfile_size > upfile_size_limit) then
        Response.Write "ERROR - ASP script says file too large, " & upfile_size & " > " & upfile_size_limit & vbLF
    else
    ' Resave file in public local directory.
		file.SaveAs Server.MapPath(uploads_dir & "\" & upfile_name)
		if file.Path <> NO_PATH then
            Response.Write "SUCCESS - " & upfile_name & " uploaded." & vbLF
        else
            Response.Write "ERROR - file.SaveAs failed! See Java Console." & vbLF
		end if
	end if
%>
