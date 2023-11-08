Sub Main

Dim username, password
username = "pi"
password = "raspberry"

Dim Hosts(9)
hosts(0) = "192.168.3.33"
hosts(1) = "192.168.3.34"
hosts(2) = "192.168.3.40"
hosts(3) = "192.168.3.41"
hosts(4) = "192.168.3.42"
hosts(5) = "192.168.3.43"
hosts(6) = "192.168.3.44"
hosts(7) = "192.168.3.45"
hosts(8) = "192.168.3.46"
hosts(9) = "192.168.3.47"


For Each HostStr In Hosts
    xsh.Session.Open ("ssh://" & username & ":" & password & "@" & HostStr)
    If xsh.Session.Connected Then
	End If
Next

End Sub
