import boto3
from ipaddress import ip_address

# Setup
# 1. Add internal registry CloudFront distribution to DISTRIBUTION_TO_BUCKET map in this source code.
# 2. Create a new Lambda in the Account with the bucket (x86, Python 3.8)
# 3. Use this source code for the lambda
# 4. Update the lambda role policy to include the ability to read S3 bucket; just GetObject is necessary.
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Sid": "VisualEditor0",
#             "Effect": "Allow",
#             "Action": "s3:GetObject",
#             "Resource": "arn:aws:s3:::INTERNAL_REGISTRY_BUCKET_NAME/*"
#         }
#     ]
# }
# 5. Role must include a Trust Relationship with "edgelambda.amazonaws.com"
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Principal": {
#                 "Service": [
#                     "edgelambda.amazonaws.com",
#                     "lambda.amazonaws.com"
#                 ]
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }
# 6. Add trigger for the function - viewer request for the internal registry's cloudfront distribution.

AWS_EC2_US_EAST_IP_RANGES = [[263579648, 263581695], [2382667912, 2382667919], [50462720, 50462975], [2713491968, 2713492479], [872677376, 872939519], [2382667856, 2382667863], [839909376, 840040447], [266126336, 266127359], [1090274560, 1090274815], [50593792, 50594047], [266132992, 266133503], [2713489920, 2713490431], [263583488, 263583743], [317194240, 317456383], [916193280, 916455423], [921436160, 921567231], [1670776832, 1670778879], [263561216, 263565311], [314507264, 314572799], [263540736, 263544831], [1796472832, 1796734975], [58982400, 59244543], [1090275840, 1090276095], [309592064, 309854207], [915406848, 915668991], [2713492992, 2713493503], [1264943104, 1264975871], [1090276352, 1090276607], [1137311744, 1137328127], [304218112, 304226303], [920780800, 920911871], [2734353664, 2734353919], [59768832, 60293119], [1086029824, 1086033919], [65011712, 66060287], [920453120, 920518655], [2382667816, 2382667823], [2382667784, 2382667791], [263548928, 263549951], [1145204736, 1145208831], [304236544, 304238591], [1666029824, 1666030079], [2713487360, 2713487871], [50595584, 50595839], [50692096, 50693119], [263581952, 263582207], [316145664, 316407807], [583008256, 584056831], [1090274304, 1090274559], [2713485824, 2713486335], [1666039552, 1666039807], [750780416, 752877567], [2713488384, 2713488895], [2734353920, 2734354431], [316669952, 316932095], [2382667776, 2382667783], [58916864, 58982399], [387186688, 387448831], [1090273280, 1090273535], [50594048, 50594303], [2713485312, 2713485823], [263557120, 263561215], [263585280, 263585535], [2713488896, 2713489407], [314441728, 314507263], [875298816, 875429887], [263565312, 263569407], [2382667904, 2382667911], [263532544, 263536639], [264308224, 264308479], [2382667800, 2382667807], [878313472, 878444543], [872415232, 872546303], [2382667896, 2382667903], [3496882176, 3496886271], [875954176, 876085247], [1666023680, 1666023935], [1666024192, 1666024447], [597229568, 597295103], [2734353408, 2734353663], [885522432, 886046719], [585105408, 586153983], [263275008, 263275519], [591881728, 591881983], [1073116928, 1073117183], [840105984, 840171519], [50463488, 50463743], [2927689728, 2927755263], [878706512, 878706527], [263577600, 263579647], [315621376, 316145663], [878703872, 878704127], [1666038528, 1666038783], [878639264, 878639279], [314310656, 314376191], [50693120, 50693631], [3091759104, 3091791871], [911212544, 911736831], [873725952, 873988095], [878627072, 878627135], [921829376, 921960447], [3635867136, 3635867647], [873398272, 873463807], [2713489408, 2713489919], [314376192, 314441727], [3495319552, 3495320063], [919601152, 919732223], [2382667824, 2382667831], [316407808, 316669951], [2713486336, 2713486847], [1666023424, 1666023679], [915931136, 915996671], [877002752, 877133823], [878639104, 878639119], [1666055680, 1666055935], [1189633024, 1189634047], [591873024, 591874047], [263274496, 263275007], [775147520, 775148543], [878051328, 878182399], [2382667864, 2382667871], [266135808, 266136063], [58851328, 58916863], [873332736, 873398271], [917241856, 917372927], [315359232, 315621375], [911736832, 911998975], [304282624, 304283647], [50463232, 50463487], [1090273792, 1090274047], [51118080, 51183615], [50529536, 50529791], [872546304, 872677375], [3091742720, 3091759103], [263569408, 263577599], [3635865600, 3635866623], [59244544, 59768831], [263582208, 263582463], [3438067712, 3438084095], [598212608, 598736895], [263530496, 263532543], [304277504, 304279551], [1210851328, 1210859519], [263544832, 263548927], [221904896, 222035967], [50594304, 50594559], [51183616, 51249151], [912031744, 912064511], [1666029312, 1666029567], [3635863552, 3635865599], [919339008, 919470079], [918814720, 918945791], [1670774784, 1670776831], [266132480, 266132991], [51380224, 51642367], [264175616, 264241151], [877133824, 877264895], [916455424, 916979711], [921305088, 921436159], [266139648, 266140159], [51249152, 51380223], [266140160, 266140671], [266136576, 266137599], [263584000, 263584255], [3328377344, 3328377599], [63963136, 65011711], [2382667848, 2382667855], [3425501184, 3425566719], [3091791872, 3091857407], [917372928, 917503999], [920649728, 920780799], [266136064, 266136575], [51642368, 51904511], [55574528, 56623103], [1090274048, 1090274303], [918945792, 919011327], [1090276608, 1090276863], [263582720, 263582975], [263550976, 263553023], [2713490944, 2713491455], [2382667888, 2382667895], [50659328, 50667519], [263583232, 263583487], [878705408, 878705663], [1210646528, 1210650623], [919732224, 919863295], [1090276096, 1090276351], [263581696, 263581951], [1679294464, 1679818751], [263528448, 263530495], [263582464, 263582719], [58720256, 58851327], [52503040, 52503295]]
DISTRIBUTION_TO_BUCKET = {
    'E2KP8SMSY4XB67': 'ci-dv2np-image-registry-us-east-1-aunteqmixxpqypvdqwbmjbiloeix', # app.ci
    'E2PBG0JIU6CTJY': 'build03-vqlvf-image-registry-us-east-1-elknekacnvmxphlxdfyvhpi',
    'E1Q1256FT1FBYD': 'build01-9hdwj-image-registry-us-east-1-nucqrmelsxtgndkbvchwdkw',
    'E1PPY7S6SRDS9W': 'build05-kwk66-image-registry-us-east-1-vuabtweixqvnbprjlctjacx',
}

# Set to None for normal operation and everything will route through
# CloudFront or S3. Set to your IP address, and you will be sent to
# S3 while everything else goes to CloudFront.
exclusive_test_for_ip = None


def lambda_handler(event, context):

    request = event['Records'][0]['cf']['request']
    event_config = event['Records'][0]['cf']['config']
    distribution_name = event_config['distributionId']
    internal_registry_bucket_name = DISTRIBUTION_TO_BUCKET.get(distribution_name, None)

    if not internal_registry_bucket_name:
        # pass right through
        return request

    request_method = request.get('method', None)
    if request_method.lower() != "get":
        # The S3 signed URL is only for GET operations.
        # The registry itself will issue HEAD when checking for images.
        # Just let CloudFront handle these.
        return request

    request_ip = request['clientIp']
    ip_as_int = int(ip_address(request_ip))

    if exclusive_test_for_ip and request_ip != exclusive_test_for_ip:
        # Someone is testing with exclusive_test_for_ip, route all
        # requests straight to CloudFront.
        return request

    found = False
    for ip_range in AWS_EC2_US_EAST_IP_RANGES:
        if exclusive_test_for_ip and exclusive_test_for_ip == request_ip:
            found = True
            break
        if ip_as_int >= ip_range[0] and ip_as_int <= ip_range[1]:
            found = True
            break

    if not found:
        # Does not appear to be a us-east IP range for EC2
        return request

    uri = request.get('uri', '')
    s3 = boto3.client('s3', region_name='us-east-1')

    # Generate a signed URL for the caller to go back to S3 and read the object
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': internal_registry_bucket_name,
            'Key': uri[1:], # Strip off /
        },
        ExpiresIn=20*60, # Expire in 20 minutes
    )

    return {
        'status': '307',
        'statusDescription': 'CostManagementRedirect',
        'headers': {
            'location': [
                {
                    'value': url
                }
            ],
        },
    }
