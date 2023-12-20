Sub Main

Dim username, password
username = "pi"
password = "raspberry"

Dim Hosts(14)
hosts(0) = "192.168.1.110"
hosts(1) = "192.168.1.117"
hosts(2) = "192.168.1.118"
hosts(3) = "192.168.1.119"
hosts(4) = "192.168.1.120"
hosts(5) = "192.168.1.121"
hosts(6) = "192.168.1.122"
hosts(7) = "192.168.1.123"
hosts(8) = "192.168.1.124"
hosts(9) = "192.168.1.125"
hosts(10) = "192.168.1.127"
hosts(11) = "192.168.1.146"
hosts(12) = "192.168.1.147"
hosts(13) = "192.168.1.148"
hosts(14) = "192.168.1.149"


For Each HostStr In Hosts
    xsh.Session.Open ("ssh://" & username & ":" & password & "@" & HostStr)
    If xsh.Session.Connected Then
	End If
Next

End Sub
