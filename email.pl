# for email
use Net::SMTP;


send_email($ARGV[0], $ARGV[1]);

sub send_email {

	my $sender = 'host-team@infineon.com';
	my @receiver = ('taufik.hidayat@infineon.com','rizki.kasmuda@infineon.com');
	my $subject = "Subject: [test $_[0]] ";
	my $emailBody = $_[1];
	my $link = "//e2asia12.intra.infineon.com/eSquare_user/kasmuda_ap/work/Database_ChipID_Checking/database";

	my $smtp = Net::SMTP->new(
		'smtp.intra.infineon.com',
		Timeout => 20,
		Debug   => 1,
	);

	#die "Initialization failed: $!" if !defined $smtp;
	if ($smtp){
		$smtp->mail( $sender );
		$smtp->to( @receiver );
		$smtp->data();
		$smtp->datasend( "To: $receiver\n");
		$smtp->datasend( "From: $sender\n");
		$smtp->datasend( "Subject: $subject \n");
		$smtp->datasend( "\n");
		$smtp->datasend("$emailBody\n");
		$smtp->datasend("$link\n");
		$smtp->datasend("\n");
		$smtp->dataend();
		$smtp->quit();
	} else {
	  die "Initialization failed: $!"
	}
					  
}