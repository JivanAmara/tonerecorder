using System;
using System.IO;
using System.Web.UI;
using System.Security.Cryptography;
using System.Text;

public partial class TestWrite : System.Web.UI.Page 
{

    protected System.Web.UI.WebControls.Label StatusLabel;
	
    // Hash an input string and return the hash as
    // a 32 character hexadecimal string.
    // This function from Microsoft's .Net Framework documentation for the MD5 class.
    private static string getMd5Hash(string input)
    {
        // Create a new instance of the MD5CryptoServiceProvider object.
        MD5 md5Hasher = MD5.Create();

        // Convert the input string to a byte array and compute the hash.
        byte[] data = md5Hasher.ComputeHash(Encoding.Default.GetBytes(input));

        // Create a new Stringbuilder to collect the bytes
        // and create a string.
        StringBuilder sBuilder = new StringBuilder();

        // Loop through each byte of the hashed data 
        // and format each one as a hexadecimal string.
        for (int i = 0; i < data.Length; i++)
        {
            sBuilder.Append(data[i].ToString("x2"));
        }

        // Return the hexadecimal string.
        return sBuilder.ToString();
    }

    protected void Page_Load(object sender, EventArgs e)
    {

	StringBuilder statusText = new StringBuilder();
	
	// NOTE: This uses a relative pathname. You may want to substitute another directory.
	String uploadDir = "../uploads/";
	statusText.Append( String.Format("Upload dir = {0}\n", uploadDir) );

	// Get client computer's IP address.
	String client_ip_address = Request.ServerVariables["REMOTE_ADDR"];
	statusText.Append( String.Format("client_ip_address = {0}\n", client_ip_address) );

	// Generate a unique filename based on the time in ticks and IP address.
	String uniq_id = System.DateTime.Now.Ticks.ToString() + client_ip_address;
	String unique_filename = Server.MapPath( uploadDir + "\\temp_" + getMd5Hash(uniq_id) + ".txt" );
	statusText.Append( String.Format("unique_filename = {0}\n", unique_filename) );

	DirectoryInfo dir = new DirectoryInfo( Server.MapPath(uploadDir) );
	if( !dir.Exists )
	{
		statusText.Append( String.Format("\nTest FAILED! Directory {0} does not exist!\n", uploadDir) );
		statusText.Append( "Please modify the code in this script to match your server folders.\n" );
	}
	else
	{
		try
		{
			StreamWriter stream = new StreamWriter( unique_filename );
			stream.WriteLine("abcd");
			stream.Close();
			statusText.Append( "\nWrite permission test PASSED!\n" );
		}
		catch( Exception )
		{
			statusText.Append( "\nWrite permission test FAILED!\n" );
			statusText.Append( String.Format("Could not write to file in directory:\n{0}\n", uploadDir) );
			statusText.Append( "Please change write permission according to the installation instructions.\n" );
		}
	}
	
	StatusLabel.Text = statusText.ToString();
	
    }
    
}
