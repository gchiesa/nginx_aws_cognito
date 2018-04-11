#!/usr/bin/env python

import pytest
from nginx_aws_cognito.entities import User

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"


@pytest.fixture
def expired_token():
    return 'eyJraWQiOiI2aXM2K2hYbHl0bmdVTjdFYUorWGpWTEVUZ1RKeEZjaUZGWVI5UTN0ZzNRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiO' \
           'iI1NDU3ZTFjOC00Y2E2LTQyNmMtYmMzNC00OWQ3ODZkNWE5NTEiLCJldmVudF9pZCI6ImI2MzJiYjA3LTNmMzMtMTFlOC1hYjViLT' \
           'U1ZGI0ZTRkYjY1YyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJ' \
           'hdXRoX3RpbWUiOjE1MjM2MzUxOTYsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5ldS13ZXN0LTEuYW1hem9uYXdzLmNvbVwv' \
           'ZXUtd2VzdC0xXzNad2labHg4WiIsImV4cCI6MTUyMzYzODc5NiwiaWF0IjoxNTIzNjM1MTk2LCJqdGkiOiJmODE3YTNiNC05ZGRlL' \
           'TRmNDAtYmIwOS03ZTAzMDUwMGY4MjQiLCJjbGllbnRfaWQiOiIyNzh0ajJwdXRzdnNnazY1Z2U3dnBydmN1bSIsInVzZXJuYW1lIj' \
           'oiZ2NfdGVzdCJ9.NiKm-wtB5i8S6Ez7y6XrwXw5CB-ap_nDdPvY6mYi87DuDbOMcqZC3bvgVVWign5w4V5onUyvvh6ePxHodVxPdk' \
           'IrGIqSzfQy5SKCNQ6K5oZ5eR-9o5AQYXd7Q7LL3ha5CZG-lvn0uTnS0dM5IpTBs8r1gjk4mqRQIR54gEa3572iMhnPZ4mBeCNfLnK' \
           '7rEaZoUZMNl2TMCM0omL1DsopQgEZu4Duj0WXqhsFTKR-AtHiC0HZ_Jnof_sKz-PJNZ_aE3774aHxxPN5GOgpOgeHELE_tZB5tVvj' \
           'MZIb98F5qOMFmbNPV9HNo4B3Tha-qhEXnS6XhUw-SxcB2YlVfwfhAQ'


@pytest.fixture
def refresh_token():
    return 'eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.W2VGtaexPj0NacWO4kEE7hCvb7l-u8qPr9MnGS' \
           'nGjqfr3dfigDC_gWkX-68rvw3VTEYDNQ2UaKSb-gjoQDLv2Ebozbpp7_Q3mAbMgZy3L6LlxNrczMH4zQ2UbCCg35usF3JbfnEZ9kK' \
           '7GvjKysd2-wdJggWK5H6wkauvE-tjUumwE8ILH2BUgXZcj3N_u9UTQCTAGyFjj-O69_tlseFDSuC99jHt48ehTh_jsfn7Sg2TuhCi' \
           'eElvflTFf51Y6hc0TYxz3KNEXaB9hfPNAA4MAAVxnE6cWH0YIp_RBJ_PYOPaZDeYYcw-o1HSeY7_T2PiOGKbjKeSzI-dPb7yYZ0Ov' \
           'A.IY-x9RowvHOngvT2.PwneLTgJc_5IMWRV43mkOE0I98wCiRVMJOs2WnAjIozoc4xxM5Vf3-sEb1gKOutbES9gDH409p6t8sev92' \
           'CL6QxwDRQ5CaTfJNHYkiKB1NJ6WdTUq0k0NbGHdU0byHi-G3eI-xxKNIcIOYho6y6UuRw8d2aPNPWUifJ8tamsW_FFeQ9tquFmkIr' \
           '-3IYOccpUEmKEYSkn8IpLiyKk14LtvguluMNexdB4pzC7GNzbUwcyT9w8T4tmhNxUo3JLjBddIGSQ1w4usJK3TcgHJA4qpUqlDed1' \
           'D2-bniuTgXkJTCi2satvZ5nOZWfRWgZLj_CPLKP6oL3oKCKaqykelprKKaJJPTNoeXaE37Fwuq8gjEBe39RWbNNlzqNPLuNl2Vp6t' \
           'AWCvb1JQa3tOCd_b7Wu1QgYrw3miflub7G2djJhEF0TYLxhusIrsVef__4cyfJxMOQa_uCFgpMyvyQwyu5txvP25t-2t7oyYFviSF' \
           '8WZahMXJnGZwM6eMkMEmKAEyV9z32f99vXSKhKnQg7fvq8oMEi7jKYwBIszaQHEGIGOGdftf3coUGm-GprHaqi03-3bT8Rr1bZrlN' \
           '-Hsk2t9pieV6ARwWN_Ysk7mEkxutEGYNJUvXDsoy4SxsE5dkV2bRDqt77wrA3Hlv7eZhhK1f4xMW2MP6Pyq6WW5zKz0_8I7T3B5bP' \
           'gnQd6MrN9Yvfvd-kNRKfaraYjEcKPdPMjMedcpBZoMWqlmn8XT6pBJ_LuPSAm_9QuHZf-LmdS1gIcEnLoCpJGoXlZdszU5poNIklw' \
           'W2K3QYYaAYP4YvJPAr-044cYXy7zvrZeMgGJOpCg-c9yA69vIROUCYEdbpXumEnbx_9SHZtAUYTyCWyNLEayP8VcFrrbIl9JZA7sq' \
           'QGn9sou_9e_nRpEezBA8yblv_zAEkPiVASbvotYpL3kyoKWpl2H8I7oGUj49B8qvNPbUlAO8ad5kidcjqCVvrIcEERjMMbUcd6X7y' \
           'JhJGZB8_YZrNum9EIwMzqR2GDrdC6ECOy6RpoEKSHTQVRENlW4yU9amxsfUj5cRVUnOTfswga4v6zkb0R7F065jWH1jJN1G8xhLHp' \
           'mtAh-MwVYn1jcAhoUWIX5zakY1luIvxno70r5_iAhQWT1XildNf95fqyCE0yE6An-yR1UBjcjfMs96rjtTKUMs65NGzGvpTUPDx0w' \
           'sF9OxopP1tC6p3WDXSZSCOo_hL3WSTewJt-Kx2AseD2c22A7ptIbh3GQJ2NHK2t-X5srmbEyMXPNm-YHibGax0bkjcIWp5v.JNXrX' \
           'COo2g5FWsAORXE81Q'


@pytest.fixture
def valid_user():
    return User('usernameA', expired_token, refresh_token, 'password', 'salt', cognito_client=None)

