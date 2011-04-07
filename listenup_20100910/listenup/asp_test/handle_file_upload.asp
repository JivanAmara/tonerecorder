<!--#include file="common_functions.asp"-->
<%
' Print information from HTML upload file form.
' (C) 2009 Mobileer Inc, www.javasonics.com
' based on handle_file_upload.php

' This must come before anything else is printed so it gets in the header.
    Response.ContentType = "text/plain"

' Instantiate an ASPUpload object
	Set upload = Server.CreateObject("Persits.Upload")
	upload.Save  ' in memory

' Get posted variables.
    userComment = strip_tags(upload.Form("userComment"))

' Extract information provided by ASPUpload object
	Set file = upload.Files("userfile")

' Print relevent file information provided by ASPUpload file object for debugging.
    Response.Write "name        = " & file.FileName & vbLF
    Response.Write "type        = " & file.ContentType & vbLF
    Response.Write "size        = " & file.Size & vbLF
    Response.Write "userComment = " & userComment & vbLF

    Response.Write vbLF & "SUCCESS file was uploaded" & vbLF
    Response.Write vbLF & "By the way, your uploaded file was not saved to the server." & vbLF
    Response.Write vbLF & "Hit BACK button in browser to continue testing." & vbLF
%>
