<%
' common_functions.asp
' (C) 2009 Mobileer Inc, www.javasonics.com

Function strip_tags(strHTML)
'Strips the HTML tags from strHTML

  Dim objRegExp, strOutput
  Set objRegExp = New Regexp

  objRegExp.IgnoreCase = True
  objRegExp.Global = True
  objRegExp.Pattern = "<(.|\n)+?>"

  'Replace all HTML tag matches with the empty string
  strOutput = objRegExp.Replace(strHTML, "")
  
  'Replace all < and > with &lt; and &gt;
  strOutput = Replace(strOutput, "<", "&lt;")
  strOutput = Replace(strOutput, ">", "&gt;")
  
  strip_tags = strOutput    'Return the value of strOutput

  Set objRegExp = Nothing
End Function

Function simple_hash(str)
  Dim maxNumber, sum, x
  maxNumber=32000
  sum=0
  For x=1 To Len(str)
 	sum=sum+Asc(Mid(str, x, 1))
  Next
  simple_hash=(sum Mod maxNumber)
End Function
%>