#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <gmp.h>

const char *key_n_hex = "a42dc4983629269abee64144ea3358efce63f646236839d87fe959efa59f2571fdbc034b1284acb241f608b4ce63851cc82f8628e0a61fc9f5b31e06603ddb5dd79eb0babb2e5d1c98c01724155ac51d3a70be4a8f037c241c1a1401105ed53d48cca16629e3fd7b43ecd683b512678b23a4b4a8881e7794b69c225a42cd92b4ea5adb01c29ee15ac376b4e62f427066c8f23d0d1465ad0c40ea41fab7674a8257c490341a9f52e35530d39c6d603f1b8cd0e1c8e967562446e3f20b119ad87773f268edaa639bdca8a2e5c4b3b5eb4400e11e01eca3397bc62e693e235643c22df0d812a6e5df6af40a49ec1570c089855a46230ba776df2963f88bd50868a9";
const char *key_e_hex = "10001";

bool validate_signature(const uint8_t signature[256], const unsigned char hash[20]) {
    mpz_t n, e, sig, decrypted_sig;
    mpz_inits(n, e, sig, decrypted_sig, NULL);
    mpz_set_str(n, key_n_hex, 16);
    mpz_set_str(e, key_e_hex, 16);
    mpz_import(sig, 1, 1, 256, 1, 0, signature);

    unsigned char decrypted_bytes[256] = {0};
    mpz_powm(decrypted_sig, sig, e, n);
    mpz_export(decrypted_bytes, NULL, 1, 256, 1, 0, decrypted_sig);
    mpz_clears(n, e, sig, decrypted_sig, NULL);

    unsigned char *decrypted_hash = decrypted_bytes + (256 - 20);
    return strcmp(hash, decrypted_hash) == 0;
}
