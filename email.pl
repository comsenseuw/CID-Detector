# for email
use Net::SMTP;


send_email($ARGV[0], $ARGV[1]);

sub send_email {

	my $sender = 'noreply@example.com';
	my @receiver = ('person1@example.com','person2@example.com');
	my $subject = "Subject: [Result $_[0]] ";
	my $emailBody = $_[1];

	my $smtp = Net::SMTP->new(
		'smtp.example.com',
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
		$smtp->datasend("\n");
		$smtp->dataend();
		$smtp->quit();
	} else {
	  die "Initialization failed: $!"
	}
					  
}